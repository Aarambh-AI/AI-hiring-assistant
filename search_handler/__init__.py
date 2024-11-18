import azure.functions as func
import json
import traceback
import logging
from bson import ObjectId
from utils import mongo_utils, openai_utils
import datetime


# Function to construct a response with consistent structure
def search_similar(job_id):
    objInstance = ObjectId(job_id)
    cosmos_util = mongo_utils.CosmosMongoUtil(collection='job_data')
    doc = cosmos_util.find_document({"_id":objInstance})
    
    embeddings = openai_utils.generate_text_embeddings(doc["jd_text"])
    # MongoDB Aggregation Pipeline
    pipeline = [
        {
            "$search": {
                "cosmosSearch": {
                    "vector": embeddings,
                    "path": "embeddings",  # Ensure embeddings field is indexed for vector search
                    "k": 20000  # Reduced the number of results to 500 (adjust based on your needs)
                },
            }
        },
        {
            "$project": {
                "similarityScore": {"$meta": "searchScore"},
                "document": "$$ROOT"
            }
        },
        # Exclude the embeddings field using $unset
        {
            "$unset": "document.embeddings"  # This removes the embeddings field from the document
        },
        # Filter results where similarityScore is above the threshold
        {
            "$match": {
                "similarityScore": {"$gte": 60.0 / 100.0}  # 60% threshold
            }
        },
        # # Optionally, limit the number of results after matching
        # {
        #     "$limit": 500  # Limit results to a reasonable number after applying threshold
        # }
    ]

    cosmos_util = mongo_utils.CosmosMongoUtil(collection='candidate_data')
    result = cosmos_util.aggregate_query(pipeline=pipeline)
    response = {"results": [], "total_results": 0}

    # List to hold documents for insertion into new collection
    docs_to_insert = []

    # Process the result and prepare the response
    for doc in result:
        response["results"].append({
            "id": doc["_id"],
            "score": doc['similarityScore'],
            "document": doc["document"]  # Include all fields from the "document"
        })

        # Prepare the document for insertion into the new collection
        doc_to_insert = {
            "job_id": job_id,  # Include the job_id to link the result to the original job
            # "candidate_id": doc["candidate_id"],  # Convert ObjectId to string
            **doc["document"],  # Include all candidate document details (excluding "job_id")
            "timestamp": datetime.datetime.utcnow()  # Add a timestamp for when the document was added
        }

        docs_to_insert.append(doc_to_insert)

    # Insert the processed documents into the new collection
    if docs_to_insert:
        try:
            new_collection_util = mongo_utils.CosmosMongoUtil(collection='ai_cache')
            new_collection_util.insert_multiple_documents(docs_to_insert)  # Insert all the documents at once
            logging.info(f"Successfully inserted {len(docs_to_insert)} documents into the 'search_results' collection.")
        except Exception as e:
            logging.error(f"Error inserting documents into 'search_results': {str(e)}")
    

    response["total_results"] = len(response["results"])
    return response



# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # Handle ObjectId
        if isinstance(obj, ObjectId):
            return str(obj)
        # Handle datetime objects
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()  # Convert datetime to ISO format string
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
        # logging.info(response)

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
