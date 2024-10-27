import azure.functions as func
import json
import traceback
import logging
from bson import ObjectId
from utils import mongo_utils, openai_utils


# Function to construct a response with consistent structure
def search_similar(job_id):
    objInstance = ObjectId(job_id)
    cosmos_util = mongo_utils.CosmosMongoUtil(collection='job_data')
    doc = cosmos_util.find_document({"_id":objInstance})
    
    embeddings = openai_utils.generate_text_embeddings(doc["jd_text"])
    pipeline = [
    {
        "$search": {
            "cosmosSearch": {
                "vector": embeddings,
                "path": "embeddings",
                "k": 3
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
    cosmos_util = mongo_utils.CosmosMongoUtil(collection='candidate_data')
    result = cosmos_util.aggregate_query(pipeline=pipeline)
    response = {"results": [], "total_results": 0}

    for doc in result:
        response["results"].append({
            "id": doc["_id"],
            "score": doc['similarityScore']
        })

    response["total_results"] = len(response["results"])
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
        job_id = req_body["job_id"]
        meta_data = req_body["meta_data"]
        response = search_similar(job_id=job_id)
        response["meta_data"] = meta_data
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
