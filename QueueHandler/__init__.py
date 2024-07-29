# from reader import file_reader
# from retriever.resume_parser import construct_hailey_response_data
import azure.functions as func
import logging
import json
from azure.storage.blob import BlobServiceClient
import os


# def process_resume():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400

#     file = request.files['file']

#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     # Save the file temporarily
#     file_path = f"/tmp/{file.filename}"
#     file.save(file_path)

#     # Read text from the file
#     text = file_reader.read_text(file_path)

#     if text:
#         json_data = construct_hailey_response_data(resume=text)
#         return jsonify(json_data)
#     else:
#         return jsonify({"error": "Failed to read text from the file"}), 500

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

    # Process the blob data (implement your processing logic here)
    print(blob_data.decode('utf-8'))


    logging.info(result)
