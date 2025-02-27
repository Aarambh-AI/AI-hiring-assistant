from pymongo import MongoClient
from typing import Optional, Dict, Any
import certifi
import re



def connect_to_mongodb(connection_string: str) -> MongoClient:
    """
    Establish connection to MongoDB
    """
    try:
        client = MongoClient(connection_string, tlsCAFile=certifi.where())
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

def fetch_candidates(filters, pagination, db_client):
    client = db_client["dev_db"]
    collection = client["candidate_data"]

    # Build base match condition with most selective fields first
    base_match = {
        "org_id": "org_2ow5pexgsO0avtK5892cjr1yUry",
    }

    # Add source filter after org_id for index efficiency
    base_match.update({
        "source": {"$ne": "proxy_curl"},
        "$or": [
            {"source": {"$ne": "signal_hire"}},
            {
                "$and": [
                    {"source": "signal_hire"},
                    {"$or": [
                        {"emails": {"$exists": True, "$ne": []}},
                        {"phones": {"$exists": True, "$ne": []}}
                    ]}
                ]
            }
        ]
    })

    # Determine which index to use based on filters
    index_hint = "org_id_1"  # default index

    # Add filters and choose appropriate index
    if filters['location']:
        base_match["currentLocation"] = {
            "$in": [re.compile(f"^{loc}", re.IGNORECASE) for loc in filters['location']]
        }
        index_hint = "org_id_1_currentLocation_1"
    
    if filters['company']:
        base_match["currentemployer"] = {
            "$in": [re.compile(f"^{comp}", re.IGNORECASE) for comp in filters['company']]
        }
        index_hint = "org_id_1_currentemployer_1"
    
    if filters['job_title']:
        base_match["role"] = {
            "$in": [re.compile(f"^{jt}", re.IGNORECASE) for jt in filters['job_title']]
        }
        index_hint = "org_id_1_role_1"
    
    if filters['skills']:
        base_match["keySkills"] = {
            "$in": [re.compile(f"^{skill}", re.IGNORECASE) for skill in filters['skills']]
        }
        index_hint = "org_id_1_keySkills_1"

    if filters['experience']:
        base_match["total_experience"] = {
            "$gte": filters['experience'][0],
            "$lte": filters['experience'][1]
        }

    if filters['gender']:
        base_match["gender"] = {
            "$exists": True,
            "$ne": None,
            "$ne": "",
            "$regex": f"^{filters['gender']}", 
            "$options": "i"
        }

    # Get total count using the same index hint
    total_candidates = collection.count_documents(base_match, hint=index_hint)

    # Get paginated results
    pipeline = [
        {"$match": base_match},
        {"$sort": {"modified_timestamp": -1}},
        {"$skip": (pagination['page'] - 1) * pagination['items_per_page']},
        {"$limit": pagination['items_per_page']},
        {
            "$project": {
                "_id": 0,
                "name": 1,
                "candidate_id": 1,
                "total_experience": 1,
                "currentemployer": 1,
                "role": 1,
                "currentLocation": 1,
                "keySkills": 1,
                "modified_timestamp": 1,
            }
        }
    ]

    # Execute aggregation with the determined index hint
    candidates = collection.aggregate(
        pipeline,
        allowDiskUse=True,
        hint=index_hint
    ).to_list(length=pagination['items_per_page'])

    return {
        "data": candidates,
        "pagination": {
            "page": pagination['page'],
            "items_per_page": pagination['items_per_page'],
            "total_candidates": total_candidates,
            "total_pages": int((total_candidates + pagination['items_per_page'] - 1) / pagination['items_per_page']),
        }
    }


def get_candidate_by_id(client: MongoClient, database_name: str, collection_name: str, candidate_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a candidate document based on candidate_id
    
    Args:
        client: MongoDB client instance
        database_name: Name of the database
        collection_name: Name of the collection
        candidate_id: ID of the candidate to fetch
    
    Returns:
        Dictionary containing candidate document or None if not found
    """
    try:
        db = client[database_name]
        collection = db[collection_name]
        
        # Fetch the document
        candidate = collection.find_one({"candidate_id": candidate_id})
        return candidate
        
    except Exception as e:
        print(f"Error fetching candidate: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Replace these with your actual MongoDB connection details
    MONGO_URI = "mongodb+srv://mongoadmin:Hiringbot_123@hiringbot-mongo-cluster-dev.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
    DATABASE_NAME = "dev_db"
    COLLECTION_NAME = "candidate_data"
    
    # Connect to MongoDB
    client = connect_to_mongodb(MONGO_URI)
    
    # Example candidate_id
    candidate_id = "f07d89fc-f9f6-4253-aab1-a12238dfe73b"
    
    # Fetch candidate
    # result = get_candidate_by_id(client, DATABASE_NAME, COLLECTION_NAME, candidate_id)
    filters = {
    "search": None,
    "job_title": None,
    "experience": [0,100],
    "skills": ["java"],
    "education": None,
    "location": None,
    "company": None,
    "gender": None
}
    pagination = {
        "page": 1,
        "items_per_page": 10    
    }
    result = fetch_candidates(filters, pagination, client)
    if result:
        print("Found candidate:", result)
    else:
        print("Candidate not found")
