from reader import file_reader
from retriever.resume_parser import construct_response_data
import azure.functions as func
import logging
import json
from azure.storage.blob import BlobServiceClient
import os
from utils import mongo_utils

def upload_resume_to_db(json_data):
    # Extract email and org_id
    email = json_data.get('emails', [])[0] if json_data.get('emails') else None
    org_id = json_data.get('org_id', "")

    if not email or not org_id:
        raise ValueError("Resume must contain an email address and organization ID.")
    
    cosmos_util = mongo_utils.CosmosMongoUtil(collection="candidate_data")
    
    # Create a query to find existing document based on both email and org_id
    existing_query = {
        "emails": email,
        "org_id": org_id
    }
    
    # Check if a document with the same email and org_id exists
    existing_resume = cosmos_util.find_document(existing_query)

    if existing_resume:
        # Update the existing document
        # Use upsert to ensure the document is updated or inserted if it doesn't exist
        cosmos_util.update_document(
            {"_id": existing_resume["_id"]}, 
            {"$set": json_data},  # Use $set to update only the provided fields
            upsert=True
        )
        logging.info(f"Resume for {email} in org {org_id} updated.")
    else:
        # Insert new document if no matching record found
        cosmos_util.insert_document(json_data)
        logging.info(f"Resume for {email} in org {org_id} inserted.")



def main(msg: func.QueueMessage):
    logging.info('Python queue trigger function processed a queue item.')
    out=json.loads(msg.get_body().decode('utf-8'))
    result = {
        'id': msg.id,
        'body': msg.get_body().decode('utf-8'),
        'expiration_time': (msg.expiration_time.isoformat()
                            if msg.expiration_time else None),
        'insertion_time': (msg.insertion_time.isoformat()
                           if msg.insertion_time else None),
        'time_next_visible': (msg.time_next_visible.isoformat()
                              if msg.time_next_visible else None),
        'pop_receipt': msg.pop_receipt,
        'dequeue_count': msg.dequeue_count
    }
    file_name = out['filename']
    meta_data = out['metadata']
    print("output is", out['filename'])

    storage_connection_string = os.environ['AzureWebJobsStorage']
     # Fetch file content from Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
    blob_client = blob_service_client.get_blob_client(container="resume-files", blob=file_name)
    blob_data = blob_client.download_blob().readall()

    # Process the blob data (processing logic here)
    try:
        file_text = file_reader.convert_file_to_text(file_name, blob_data)
        if file_text:
            json_data = construct_response_data(resume=file_text, container="resume-files", blob=file_name, meta_data = meta_data)

            upload_resume_to_db(json_data=json_data)
            logging.info(json_data)
        else:
            logging.error({"error": "Failed to read text from the file"})

    except ValueError as e:
        print(f"Error: {str(e)}")


    logging.info(result)

