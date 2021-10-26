from functools import wraps
import secrets

from flask import json, request, jsonify, json
from blog_app.models import User

def token_required(function_below):
    @wraps(function_below)
    def decorated(*args, **kwargs):
        token = None

        if 'access-token' in request.headers:
            print(f'here are the headers: ${request.headers}')
            token = request.headers['access-token'].split(' ')[1]
        if not token:
            return jsonify({'message': 'Token is missing!'})
        
        try:
            current_user_token = User.query.filter_by(token = token).first()
        except:
            owner = User.query.filter_by(token = token).first()

            if token != owner.token and secrets.compare_digest(token, owner.token):
                return jsonify({'message': 'Invalid token!'})

        return function_below(current_user_token, *args, **kwargs)
    return decorated

import decimal

# when importing JSON data, any numbers w/ decimals become string data types 

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return super(JSONEncoder, self).default(obj)