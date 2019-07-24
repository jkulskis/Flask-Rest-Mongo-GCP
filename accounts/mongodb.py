from bson.objectid import ObjectId
from flask_pymongo import PyMongo
import time
import random
import secrets

mongo = None

def _id(id):
    if not isinstance(id, ObjectId):
        return ObjectId(id)
    return id

def from_mongo(data):
    """
    Translates the MongoDB dictionary format into the format that's expected
    by the application.
    """
    if not data:
        return None

    data['id'] = str(data['_id'])
    data.pop('_id')
    return data

def init_app(app):
    global mongo

    mongo = PyMongo(app)
    mongo.init_app(app)

def get_key(id):
    result = mongo.db.keys.find_one({'_id': _id(id)})
    return from_mongo(result)

def valid_keys(admin=False, detailed=False):
    if detailed:
        if admin:
            return [{'Hash' : key['hash'], 'Admin' : key['admin']} for key in mongo.db.keys.find({'admin' : True})]
        else:
            return [{'Hash' : key['hash'], 'Admin' : key['admin']} for key in mongo.db.keys.find()]
    else:
        if admin:
            return [key['hash'] for key in mongo.db.keys.find({'admin' : True})]
        else:
            return [key['hash'] for key in mongo.db.keys.find()]

def add_key(key_hash, admin=False):
    if not key_hash:
        key_hash = secrets.token_urlsafe(16)
    key_dict = dict.fromkeys(['hash', 'time_created', 'admin'])
    key_dict['hash'] = key_hash
    key_dict['time_created'] = time.time()
    key_dict['admin'] = admin
    if key_hash in valid_keys():
        return 'Error: Hash "{}" already exists'.format(key_hash)
    result = mongo.db.keys.insert_one(key_dict)
    return_string = '<br/>'
    for k, v in get_key(result.inserted_id).items():
        return_string += '<br/>'
        return_string += '{} : {}'.format(k, v)
    return 'Succesfully Added Key: {}'.format(return_string)

def remove_key(key_hash):
    key = mongo.db.keys.find_one({'hash' : key_hash})
    if not key:
        return 'Error: Key Not Found'
    else:
        delete(key['_id'])
        return 'Removed {}'.format(key_hash)

def update_account(number, **kwargs):
    pass

def delete(id):
    mongo.db.keys.delete_one({'_id': _id(id)})
