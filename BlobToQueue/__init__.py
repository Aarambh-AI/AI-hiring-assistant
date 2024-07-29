import azure.functions as func
import logging
import json


def main(myblob: func.InputStream, msg: func.Out[str])-> func.HttpResponse:
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")
    
    
    try:
        message = json.dumps({"filename":myblob.name, "size":myblob.length})
        msg.set(message)
        logging.info(f"Message sent to queue: {message}")
        

    except Exception as e:
        logging.error(f"Error sending message to queue: {str(e)}")