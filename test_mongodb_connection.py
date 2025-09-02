# test_mongodb_connection.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Test connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('MONGO_DB_NAME')]
collection = db[os.getenv('MONGO_COLLECTION')]

# Test insert
test_doc = {"message": "Hello Newton!", "timestamp": "2025-09-02"}
result = collection.insert_one(test_doc)
print(f"Inserted document with ID: {result.inserted_id}")

# Test query
doc = collection.find_one({"message": "Hello Newton!"})
print(f"Found document: {doc}")

# Close connection
client.close()
