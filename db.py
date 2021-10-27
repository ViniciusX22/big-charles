from pymongo import MongoClient
from os import getenv

client = MongoClient(getenv('MONGODB_URI'))


def get_collection():
    db = client['bigcharles']
    return db['patterns']


def get_delimiter(guild_id):
    config = client['bigcharles']['configs'].find({'guild_id': guild_id})[0]
    return config['delimiter']


def set_delimiter(args, guild_id):
    if len(args) != 1: return
    configs = client['bigcharles']['configs']
    configs.update_one({'guild_id': guild_id}, {
                       '$set': {'delimiter': args[0]}}, upsert=True)


def get_patterns(guild_id):
    return get_collection().find({'guild_id': guild_id})


def set_pattern(args, guild_id):
    if len(args) < 2: return
    regex = args[0]
    response = ' '.join(args[1:])

    get_collection().update_one({'value': regex, 'guild_id': guild_id}, {
        '$set': {'response': response}}, upsert=True)


def remove_pattern(args, guild_id):
    if len(args) < 1: return
    regex = args[0]
    get_collection().delete_one({'value': regex, 'guild_id': guild_id})
