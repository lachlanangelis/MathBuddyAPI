from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify, current_app, Blueprint, request
import jwt
import MySQLdb.cursors
from env_var import api_key

decorator_routes = Blueprint('decorator_routes', __name__)

def get_mysql():
    with current_app.app_context():
        print("Accessing MySQL database configuration...")
        return current_app.config['mysql']

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_jwt_identity()
            print(f"User retrieved from JWT: {user}")
            if user and user['role'] == role:
                return f(*args, **kwargs)
            else:
                print("Access forbidden: insufficient rights")
                return jsonify({"message": "Access forbidden: insufficient rights"}), 403

        return decorated_function

    return decorator

def get_role(jwt_token):
    try:
        print(f"Decoding JWT token: {jwt_token}")
        decoded_token = jwt.decode(jwt_token, api_key, algorithms=["HS256"])
        identity = decoded_token.get('sub')
        if identity:
            role = identity.get('role')
            email = identity.get('email')
            print(f"Decoded identity: role={role}, email={email}")
            return {"role": role, "email": email}
        else:
            print("No identity found in token")
            return None
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return {"message": "Token expired"}, 401
    except jwt.InvalidTokenError:
        print("Invalid token")
        return {"message": "Invalid token"}, 401
    except Exception as e:
        print(f"Error decoding token: {str(e)}")
        return {"message": str(e)}, 401

def get_email(jwt_token):
    try:
        print(f"Decoding JWT token: {jwt_token}")
        decoded_token = jwt.decode(jwt_token, api_key, algorithms=["HS256"])
        identity = decoded_token.get('sub')
        if identity:
            email = identity.get('email')
            print(f"Decoded email: {email}")
            return email
        else:
            print("No identity found in token")
            return None
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return {"message": "Token expired"}, 401
    except jwt.InvalidTokenError:
        print("Invalid token")
        return {"message": "Invalid token"}, 401
    except Exception as e:
        print(f"Error decoding token: {str(e)}")
        return {"message": str(e)}, 401

def get_id(jwt_token):
    try:
        print(f"Decoding JWT token: {jwt_token}")
        decoded_token = jwt.decode(jwt_token, api_key, algorithms=["HS256"])
        sub = decoded_token.get('sub', {})
        if sub:
            role = sub.get('role')
            user_id = sub.get('user_id')
            print(f"Decoded sub: role={role}, user_id={user_id}")
            if role == 'student':
                return get_student_id(user_id)
            elif role == 'teacher':
                return get_teacher_id(user_id)
            elif role == 'parent':
                return get_parent_id(user_id)
            else:
                raise ValueError("Unknown role")
        else:
            raise ValueError("Invalid token")
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return {"error": "Token has expired"}, 401
    except jwt.InvalidTokenError:
        print("Invalid token")
        return {"error": "Invalid token"}, 401
    except Exception as e:
        print(f"Error decoding token: {str(e)}")
        return {"error": str(e)}, 500

def get_student_id(user_id):
    try:
        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        print(f"Querying for student_id with user_id={user_id}")
        query = "SELECT student_id FROM students WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        stu_id = cursor.fetchone()
        print(f"Student ID retrieved: {stu_id}")
        cursor.close()
        return stu_id["student_id"]
    except Exception as e:
        print(f"Error querying student ID: {str(e)}")
        return None

def get_teacher_id(user_id):
    # Implement this function to retrieve teacher_id based on user_id
    pass

def get_parent_id(user_id):
    # Implement this function to retrieve parent_id based on user_id
    pass

# Example route to get the role from a JWT token
@decorator_routes.route('/get_role', methods=['POST'])
def role_route():
    jwt_token = request.json.get('token')
    if not jwt_token:
        return jsonify({"message": "Token is required"}), 400

    result = get_role(jwt_token)
    return jsonify(result)

# Example route to get the email from a JWT token
@decorator_routes.route('/get_email', methods=['POST'])
def email_route():
    jwt_token = request.json.get('token')
    if not jwt_token:
        return jsonify({"message": "Token is required"}), 400

    email = get_email(jwt_token)
    if email:
        return jsonify({"email": email})
    else:
        return jsonify({"message": "Email not found"}), 404

# Example route to get the user ID from a JWT token
@decorator_routes.route('/get_id', methods=['POST'])
def id_route():
    jwt_token = request.json.get('token')
    if not jwt_token:
        return jsonify({"message": "Token is required"}), 400

    user_id = get_id(jwt_token)
    if isinstance(user_id, dict):  # Check if the response is an error message
        return jsonify(user_id), 401
    else:
        return jsonify({"user_id": user_id})
