import azure.functions as func
import json
import traceback
import logging
from bson import ObjectId
from utils import mongo_utils, openai_utils


# Function to construct a response with consistent structure
def search_similar(text):
    
    embeddings = openai_utils.generate_text_embeddings(text)
    pipeline = [
    {
        "$search": {
            "cosmosSearch": {
                "vector": embeddings,
                "path": "embeddings",
                "k": 2
            },
            "returnStoredSource": True
        }
    },
    {
        "$project": {
            "similarityScore": {
                "$meta": "searchScore"
            },
            "document": "$$ROOT"
        }
    }
]
    cosmos_util = mongo_utils.CosmosMongoUtil()
    result = cosmos_util.aggregate_query(pipeline=pipeline)
    id_list, score_list = [], []
    response = {"id_list":[],"score_list":[]}

    for doc in result:
       id_list.append(doc["_id"])
       score_list.append(doc['similarityScore'])
    response["id_list"]= id_list
    response["score_list"]=score_list
    return response



# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(JSONEncoder, self).default(obj)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Handles incoming requests, processes queries, and constructs responses."""

    logging.info("search handler endpoint triggered")

    try:
        req_body = req.get_json()
        logging.info(f"Incoming Request - {req_body}")
        text = req_body["text"]
        response = search_similar(text=text)
        
        logging.info(response)

        return func.HttpResponse(
            body=json.dumps(response,cls=JSONEncoder),
            mimetype="application/json",
            status_code=200,
        )

    except Exception as ex:
        logging.exception(traceback.format_exc())
        return func.HttpResponse(
            body=json.dumps({"response": str(ex)}),
            mimetype="application/json",
            status_code=400,
        )
