# models/__init__.py
from pymongo import MongoClient
from config import Config

# MongoDB connection
client = MongoClient(Config.MONGO_URI)
db = client[Config.DB_NAME]

# Create collections if they don't exist
if "users" not in db.list_collection_names():
    db.create_collection("users")

if "products" not in db.list_collection_names():
    db.create_collection("products")

if "messages" not in db.list_collection_names():
    db.create_collection("messages")

if "contracts" not in db.list_collection_names():
    db.create_collection("contracts")

if "auctions" not in db.list_collection_names():
    db.create_collection("auctions")

if "notifications" not in db.list_collection_names():
    db.create_collection("notifications")