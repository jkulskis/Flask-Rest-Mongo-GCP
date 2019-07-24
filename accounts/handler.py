from flask import Blueprint, redirect, render_template, request, url_for
from functools import wraps, partial
import accounts.mongodb as mongodb

handler = Blueprint('handler', __name__)

def validate_user(function, admin=False):
    @wraps(function)
    def check_key(*args, **kwargs):
        if request.args.get('user'):
            if request.args.get('user') in mongodb.valid_keys(admin=admin):
                return function(*args, **kwargs)
            else:
                if admin and request.args.get('user') in mongodb.valid_keys():
                    return 'User must be admin for this operation'
                return 'Invalid user hash'
        else:
            return 'Please specify a user hash'
    return check_key

validate_admin = partial(validate_user, admin=True)

@handler.route("/")
def index():
    return 'No operation specified'

@handler.route("keys/validate")
@validate_user
def validate_key():
    return 'Valid API Key'

@handler.route("keys/add")
@validate_admin # only admins can add new keys
def add_key():
    key_hash = request.args.get('hash')
    if key_hash and len(key_hash) < 3:
        return 'Error: Hash must be at least 3 characters in length'
    if request.args.get('admin'):
        if request.args.get('admin') == 'True':
            return mongodb.add_key(key_hash, admin=True)
    return mongodb.add_key(key_hash)

@handler.route("keys/remove")
@validate_admin # only admins can remove keys
def remove_key():
    key_hash = request.args.get('hash')
    if not key_hash:
        return 'Error: Specify a hash to remove'
    return mongodb.remove_key(key_hash)

@handler.route('keys/list')
@validate_admin # only admins can list keys
def list_keys():
    return_string = ''
    for key in mongodb.valid_keys(detailed=True, admin=request.args.get('admin')):
        for k, v in key.items():
            return_string += '{} : {}</br>'.format(k, v)
        return_string += '<br/>'
    return return_string
