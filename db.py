from pymongo import MongoClient
import config


mongo_client = MongoClient()
db = mongo_client[config.database]
collection = db[config.collection]
