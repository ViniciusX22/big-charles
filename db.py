from pymongo import MongoClient
from os import getenv

client = MongoClient(getenv('MONGODB_URI'))


def is_int(value):
    try:
        s = int(value)
        return True
    except Exception:
        return False

def get_collection():
    db = client['bigcharles']
    return db['patterns']


def get_delimiter(guild_id):
    config = client['bigcharles']['configs'].find({'guild_id': guild_id})[0]
    return config['delimiter']


def set_delimiter(args, guild_id):
    if len(args) != 1:
        return
    configs = client['bigcharles']['configs']
    configs.update_one({'guild_id': guild_id}, {
                       '$set': {'delimiter': args[0]}}, upsert=True)


def get_patterns(guild_id):
    return get_collection().find({'guild_id': guild_id})


def set_pattern(args, guild_id):
    if len(args) < 2:
        return
    regex = args[0]
    response = args[1]
    chance = int(args[2]) if len(args) > 2 else 100

    get_collection().update_one({'value': regex, 'guild_id': guild_id}, {
        '$set': {'response': response, 'chance': chance}}, upsert=True)


def remove_pattern(args, guild_id):
    if len(args) < 1:
        return
    regex = args[0]
    patterns = get_collection()
    result = patterns.delete_one({'value': regex, 'guild_id': guild_id})
    if result.deleted_count == 0 and is_int(regex):
        # tries to delete pattern at position <regex>
        pattern = patterns.find_one({'guild_id': guild_id}, skip=int(regex)-1)
        if pattern:
            patterns.delete_one({'_id': pattern['_id'] })
