from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
import logging
import os

class CosmosMongoUtil:
    _instance = None
    _collections = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CosmosMongoUtil, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.connection_string = "mongodb+srv://mongoadmin:Hiringbot_123@hiringbot-mongo-cluster-dev.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
            self.database_name = "dev_db"
            self.client = None
            self.db = None
            self._connect()
            self._initialized = True

    def _connect(self):
        try:
            # Add SSL configuration
            self.client = MongoClient(
                self.connection_string,
                tlsAllowInvalidCertificates=True  # For development environments
                # For production, use proper SSL certificates:
                # ssl_ca_certs='/path/to/ca.pem'  # Uncomment and set proper path in production
            )
            self.db = self.client[self.database_name]
            logging.info("Connected to MongoDB")
        except ConnectionFailure as e:
            logging.error(f"Could not connect to MongoDB: {str(e)}")
            raise

    def get_collection(self, collection_name):
        if collection_name not in self._collections:
            self._collections[collection_name] = MongoCollection(self.db[collection_name])
        return self._collections[collection_name]

class MongoCollection:
    def __init__(self, collection):
        self.collection = collection

    def insert_document(self, document):
        try:
            result = self.collection.insert_one(document)
            logging.info(f"Document inserted with id: {result.inserted_id}")
            return result.inserted_id
        except PyMongoError as e:
            logging.error(f"Error inserting document: {str(e)}")
            raise

    def update_document(self, query, update_data):
        try:
            result = self.collection.update_one(query, {'$set': update_data})
            if result.modified_count > 0:
                logging.info(f"Document updated with id: {query['_id']}")
            else:
                logging.info("No documents matched the query. Document not updated.")
            return result.modified_count
        except PyMongoError as e:
            logging.error(f"Error updating document: {str(e)}")
            raise

    def insert_multiple_documents(self, documents):
        try:
            result = self.collection.insert_many(documents)
            # logging.info(f"Documents inserted with ids: {result.inserted_ids}")
            return result.inserted_ids
        except PyMongoError as e:
            logging.error(f"Error inserting documents: {str(e)}")
            raise

    def find_document(self, query):
        try:
            document = self.collection.find_one(query)
            if document:
                document_id = document["_id"]
                logging.info(f"Document found: {document_id}")
            else:
                logging.info("No document matches the query")
            return document
        except PyMongoError as e:
            logging.error(f"Error finding document: {str(e)}")
            raise
    
    def find_many(self, query):
        try:
            document = self.collection.find(query)
            if document:
                logging.info("Documents found")
            else:
                logging.info("No document matches the query")
            return document
        except PyMongoError as e:
            logging.error(f"Error finding document: {str(e)}")
            raise

    def delete_document(self, query):
        try:
            result = self.collection.delete_one(query)
            if result.deleted_count > 0:
                logging.info(f"Document deleted: {query}")
            else:
                logging.info("No document matches the query")
            return result.deleted_count
        except PyMongoError as e:
            logging.error(f"Error deleting document: {str(e)}")
            raise
    
    def delete_many(self,query):
        try:
            result = self.collection.delete_many(query)
            if result.deleted_count > 0:
                logging.info(f"Documents deleted: {query}")
            else:
                logging.info("No documents matches the query")
            return result.deleted_count
        except PyMongoError as e:
            logging.error(f"Error deleting documents: {str(e)}")
            raise

    
    def aggregate_query(self, pipeline):
        try:
            result = self.collection.aggregate(pipeline)
            if result:
                logging.info("results found")
            else:
                logging.info("No results found")
            return result
        except PyMongoError as e:
            logging.error(f"Error running aggregate query: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    database_name = "dev_data"
    collection_name = "job_data"

    mongo_util = CosmosMongoUtil()

    # Get different collections
    users_collection = mongo_util.get_collection("job_data")
    # orders_collection = mongo_util.get_collection("orders")

    # Use collections
    users_collection.insert_document({"name": "John"})
    # orders_collection.insert_document({"order_id": "123"})
    # Insert a single document
    doc = {"name": "John Doe", "age": 30, "city": "New York"}
    users_collection.insert_document(doc)

    # Insert multiple documents
    docs = [
        {"name": "Alice", "age": 25, "city": "Los Angeles"},
        {"name": "Bob", "age": 35, "city": "Chicago"},
        {"name": "Charlie", "age": 28, "city": "San Francisco"}
    ]
    users_collection.insert_multiple_documents(docs)

    # Find a document
    query = {"name": "John Doe"}
    found_doc = users_collection.find_document(query)
    print(found_doc)

    # Delete a doc