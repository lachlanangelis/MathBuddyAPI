from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_jwt_identity()
            if user and user['role'] == role:
                return f(*args, **kwargs)
            else:
                return jsonify({"message": "Access forbidden: insufficient rights"}), 403
        return decorated_function
    return decorator
