from reader import file_reader
from retriever.resume_parser import construct_response_data
import azure.functions as func
import logging
import json
from azure.storage.blob import BlobServiceClient
import os
from utils import mongo_utils
import traceback

def upload_resume_to_db(json_data):
    """
    Uploads or updates a resume document in the Cosmos DB database.
    
    Args:
        json_data (dict): Resume data in JSON format containing parsed resume information.
                         Expected to potentially contain 'emails' and 'org_id' fields.
    
    Returns:
        None
    
    Raises:
        ValueError: If organization ID (org_id) is not provided in the json_data.
    """
    # Extract the first email from the emails list if it exists, otherwise None
    # This handles cases where emails may be missing or empty
    email = json_data.get('emails', [])[0] if json_data.get('emails') else None
    
    # Get the organization ID, defaulting to empty string if not found
    # org_id is required for proper document organization and access control
    org_id = json_data.get('org_id', "")

    # Validate that org_id exists since it's a required field
    # This ensures data integrity and proper organization attribution
    if not org_id:
        raise ValueError("Resume must contain an organization ID.")
    
    # Initialize connection to Cosmos DB with the candidate_data collection
    # This collection stores all resume information
    cosmos_util = mongo_utils.CosmosMongoUtil(collection="candidate_data")
    
    # Handle case where no email is present in the resume
    if not email:
        # For resumes without emails, we simply insert as new documents
        # since we cannot track duplicates without an email identifier
        cosmos_util.insert_document(json_data)
        logging.info(f"New resume inserted (no email present). Org ID: {org_id}")
    else:
        # When email exists, we need to check for existing records
        # Create query to find any existing resume with same email and org_id
        # This ensures we don't create duplicates within the same organization
        existing_query = {
            "emails": email,
            "org_id": org_id
        }
        
        # Query the database to check for existing resume
        existing_resume = cosmos_util.find_document(existing_query)

        if existing_resume:
            # If resume exists, update it with new information
            # This keeps the resume data current while maintaining the same document ID
            cosmos_util.update_document(
                {"_id": existing_resume["_id"]}, 
                json_data  # Complete document update with new data
            )
            logging.info(f"Resume for {email} in org {org_id} updated.")
        else:
            # If no existing resume found, insert as new document
            # This creates a new record for this email/org combination
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
    
    logging.info(f"Processing file: {out['filename']}")

    storage_connection_string = os.environ['AzureWebJobsStorage']
     # Fetch file content from Blob Storage
    blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
    blob_client = blob_service_client.get_blob_client(container="resume-files", blob=file_name)
    blob_data = blob_client.download_blob().readall()

    # Process the blob data (processing logic here)
    try:

        file_text = file_reader.convert_file_to_text(file_name, blob_data)
        
        if file_text:
            if file_name.lower().endswith(('.xlsx', '.xls')):
                for candidate in file_text:
                    json_data = construct_response_data(resume=candidate, container="resume-files", blob=file_name, meta_data = meta_data)
                    upload_resume_to_db(json_data=json_data)
            elif file_name.lower().endswith('.csv'):
                for candidate in file_text:
                    json_data = construct_response_data(resume=candidate, container="resume-files", blob=file_name, meta_data = meta_data)
                    upload_resume_to_db(json_data=json_data)
            else:
                json_data = construct_response_data(resume=file_text, container="resume-files", blob=file_name, meta_data = meta_data)

            upload_resume_to_db(json_data=json_data)
            logging.info("Successfully uploaded resume to Cosmos DB.")
        else:
            logging.error({"error": "Failed to read text from the file"})

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        traceback.print_exc()

    logging.info(result)

