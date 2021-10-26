from pymongo import MongoClient
from os import getenv

client = MongoClient(getenv('MONGODB_URI'))

def get_collection():
    db = client['bigcharles']
    return db['patterns']

def get_patterns():
    return get_collection().find()
    
def add_pattern(args):
    regex, response = args
    pattern = {
        'value': regex,
        'response': response
    }
    get_collection().insert_one(pattern)