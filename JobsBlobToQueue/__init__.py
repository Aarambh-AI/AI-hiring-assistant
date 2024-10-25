import azure.functions as func
import logging
import json


def main(myblob: func.InputStream, msg: func.Out[str])-> func.HttpResponse:
    logging.info(f"Python blob trigger function processed job-files blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")
    
    blob_name = myblob.name.split('/')[-1]
    try:
        message = json.dumps({"filename":blob_name, "size":myblob.length, "metadata":myblob.metadata})
        msg.set(message)
        logging.info(f"Message sent to queue: {message}")
        

    except Exception as e:
        logging.error(f"Error sending message to queue: {str(e)}")