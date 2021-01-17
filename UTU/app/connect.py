from app import app
from pymongo import MongoClient

class Connect(object):
    @staticmethod    
    def get_connection():
        return MongoClient(f"{app.config['MONGO_URI']}")