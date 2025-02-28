import azure.functions as func
import json
import traceback
import logging
from bson import ObjectId
from utils import mongo_utils, openai_utils
import datetime


# Function to construct a response with consistent structure
def search_similar(job_id):
    try:
        # Initialize MongoDB connections
        cosmos_util = mongo_utils.CosmosMongoUtil()
        job_collection = cosmos_util.get_collection('job_data')
        candidate_collection = cosmos_util.get_collection('candidate_data')
        ai_cache_collection = cosmos_util.get_collection('ai_cache')

        # Fetch job document and generate embeddings
        doc = job_collection.find_document({"_id": ObjectId(job_id)})
        if not doc:
            raise ValueError(f"Job with ID {job_id} not found")
        
        embeddings = openai_utils.generate_text_embeddings(doc["jd_text"])
        
        # Optimized MongoDB Aggregation Pipeline
        # MongoDB Aggregation Pipeline
        pipeline = [
            {
                "$search": {
                    "cosmosSearch": {
                        "vector": embeddings,
                        "path": "embeddings",  # Ensure embeddings field is indexed for vector search
                        "k": 10000  # Reduced the number of results to 500 (adjust based on your needs)
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
                    "similarityScore": {"$gte": 75.0 / 100.0}  # 60% threshold
                }
            },
            # # Optionally, limit the number of results after matching
            # {
            #     "$limit": 500  # Limit results to a reasonable number after applying threshold
            # }
        ]

        # Process results in batches
        results = []
        docs_to_insert = []
        current_time = datetime.datetime.utcnow()

        for doc in candidate_collection.aggregate_query(pipeline):
            doc_copy = doc["document"]
            
            # Prepare response document
            results.append({
                "id": doc["document"].get("_id"),
                "score": doc['similarityScore'],
                "document": doc_copy
            })

            # Prepare cache document
            docs_to_insert.append({
                "job_id": job_id,
                "score": doc['similarityScore'],
                **doc_copy,
                "timestamp": current_time
            })

        # Batch process cache updates
        if docs_to_insert:
            # Clear existing cache
            ai_cache_collection.delete_many({"job_id": job_id})
            
            # Insert new results in batches
            batch_size = 1000
            for i in range(0, len(docs_to_insert), batch_size):
                batch = docs_to_insert[i:i + batch_size]
                ai_cache_collection.insert_multiple_documents(batch)
            
            logging.info(f"Cached {len(docs_to_insert)} results for job {job_id}")

        return {
            "results": results,
            "total_results": len(results),
            "processing_time": (datetime.datetime.utcnow() - current_time).total_seconds()
        }

    except Exception as e:
        logging.error(f"Error in search_similar: {str(e)}")
        raise



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
