from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
import logging
import os

class CosmosMongoUtil:
    def __init__(self):
        self.connection_string = "mongodb://cosmos-db-mongodb:XLeGElgW8prWnDA33bWYtyKymmTKXWwu0dC7AessAcCX3UzQ1uY8dFuZgzSqktBghGf03Fi7bmH3ACDbsrnUJg==@cosmos-db-mongodb.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@cosmos-db-mongodb@"
        self.database_name = "Dev-Db"
        self.collection_name = "Candidate_Data"
        self.client = None
        self.db = None
        self.collection = None
        self._connect()

    def _connect(self):
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            logging.info("Connected to MongoDB")
        except ConnectionFailure as e:
            logging.error(f"Could not connect to MongoDB: {str(e)}")
            raise

    def insert_document(self, document):
        try:
            result = self.collection.insert_one(document)
            logging.info(f"Document inserted with id: {result.inserted_id}")
            return result.inserted_id
        except PyMongoError as e:
            logging.error(f"Error inserting document: {str(e)}")
            raise

    def insert_multiple_documents(self, documents):
        try:
            result = self.collection.insert_many(documents)
            logging.info(f"Documents inserted with ids: {result.inserted_ids}")
            return result.inserted_ids
        except PyMongoError as e:
            logging.error(f"Error inserting documents: {str(e)}")
            raise

    def find_document(self, query):
        try:
            document = self.collection.find_one(query)
            if document:
                logging.info(f"Document found: {document}")
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

if __name__ == "__main__":
    # Example usage
    connection_string = os.getenv("COSMOS_CONNECTION_STRING")
    database_name = "your_database_name"
    collection_name = "your_collection_name"

    cosmos_util = CosmosMongoUtil(connection_string, database_name, collection_name)

    # Insert a single document
    doc = {"name": "John Doe", "age": 30, "city": "New York"}
    cosmos_util.insert_document(doc)

    # Insert multiple documents
    docs = [
        {"name": "Alice", "age": 25, "city": "Los Angeles"},
        {"name": "Bob", "age": 35, "city": "Chicago"},
        {"name": "Charlie", "age": 28, "city": "San Francisco"}
    ]
    cosmos_util.insert_multiple_documents(docs)

    # Find a document
    query = {"name": "John Doe"}
    found_doc = cosmos_util.find_document(query)
    print(found_doc)

    # Delete a doc