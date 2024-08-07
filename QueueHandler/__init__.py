from reader import file_reader
from retriever.resume_parser import construct_response_data
import azure.functions as func
import logging
import json
from azure.storage.blob import BlobServiceClient
import os
from utils import mongo_utils


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
            json_data = construct_response_data(resume=file_text)
            cosmos_util = mongo_utils.CosmosMongoUtil()
            cosmos_util.insert_document(json_data)
            logging.info(json_data)
        else:
            logging.error({"error": "Failed to read text from the file"})

        print(file_text)
    except ValueError as e:
        print(f"Error: {str(e)}")


    logging.info(result)
