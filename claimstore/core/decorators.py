from functools import wraps
from flask import jsonify, request


def only_json(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        if 'application/json' in request.headers['Content-Type']:
            return f(*args, **kwds)
        return jsonify({'status': 'error', 'message': 'Only JSON requests accepted'}), 400
    return wrapper
