from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify, current_app, Blueprint, request
import jwt
import MySQLdb.cursors
from env_var import api_key

# Blueprint to define the routes for the decorators
decorator_routes = Blueprint('decorator_routes', __name__)

# Function to access MySQL database configuration from Flask's app context
def get_mysql():
    with current_app.app_context():
        return current_app.config['mysql']

# Decorator to enforce role-based access control
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_jwt_identity()  # Retrieve user identity from JWT
            if user and user['role'] == role:  # Check if the user has the required role
                return f(*args, **kwargs)
            else:
                return jsonify({"message": "Access forbidden: insufficient rights"}), 403  # Forbidden if role mismatch

        return decorated_function
    return decorator

# Function to decode JWT and retrieve role and email from the token
def get_role(jwt_token):
    try:
        decoded_token = jwt.decode(jwt_token, api_key, algorithms=["HS256"])  # Decode JWT token
        identity = decoded_token.get('sub')  # Retrieve identity (sub) from the token
        if identity:
            return {"role": identity.get('role'), "email": identity.get('email')}  # Return role and email
        else:
            return None  # No identity found in the token
    except jwt.ExpiredSignatureError:
        return {"message": "Token expired"}, 401  # Token has expired
    except jwt.InvalidTokenError:
        return {"message": "Invalid token"}, 401  # Token is invalid
    except Exception as e:
        return {"message": str(e)}, 401  # Handle other exceptions

# Function to decode JWT and retrieve email from the token
def get_email(jwt_token):
    try:
        decoded_token = jwt.decode(jwt_token, api_key, algorithms=["HS256"])  # Decode JWT token
        identity = decoded_token.get('sub')  # Retrieve identity (sub) from the token
        if identity:
            return identity.get('email')  # Return email
        else:
            return None  # No identity found in the token
    except jwt.ExpiredSignatureError:
        return {"message": "Token expired"}, 401  # Token has expired
    except jwt.InvalidTokenError:
        return {"message": "Invalid token"}, 401  # Token is invalid
    except Exception as e:
        return {"message": str(e)}, 401  # Handle other exceptions

# Function to decode JWT and retrieve user ID based on role (student, teacher, parent)
def get_id(jwt_token):
    try:
        decoded_token = jwt.decode(jwt_token, api_key, algorithms=["HS256"])  # Decode JWT token
        sub = decoded_token.get('sub', {})  # Retrieve the 'sub' (identity) from the token
        if sub:
            role = sub.get('role')
            user_id = sub.get('user_id')
            # Route to the correct function based on the user's role
            if role == 'student':
                return get_student_id(user_id)
            elif role == 'teacher':
                return get_teacher_id(user_id)
            elif role == 'parent':
                return get_parent_id(user_id)
            else:
                raise ValueError("Unknown role")  # Raise error for unknown roles
        else:
            raise ValueError("Invalid token")  # Invalid token if 'sub' not found
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}, 401  # Token has expired
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}, 401  # Token is invalid
    except Exception as e:
        return {"error": str(e)}, 500  # Handle other exceptions

# Function to decode JWT and retrieve user ID
def get_uid(jwt_token):
    try:
        decoded_token = jwt.decode(jwt_token, api_key, algorithms=["HS256"])  # Decode JWT token
        sub = decoded_token.get('sub', {})  # Retrieve the 'sub' (identity) from the token
        if sub:
            return sub.get('user_id')  # Return user ID
    except Exception as e:
        return None  # Handle any exceptions by returning None

# Retrieve student ID from the database using the user's ID
def get_student_id(user_id):
    try:
        mysql = get_mysql()  # Get MySQL connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = "SELECT student_id FROM students WHERE user_id = %s"
        cursor.execute(query, (user_id,))  # Execute query to fetch student ID
        stu_id = cursor.fetchone()
        cursor.close()
        return stu_id["student_id"]  # Return student ID
    except Exception as e:
        return None  # Handle any exceptions by returning None

# Retrieve teacher ID from the database using the user's ID
def get_teacher_id(user_id):
    try:
        mysql = get_mysql()  # Get MySQL connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = "SELECT teacher_id FROM teachers WHERE user_id = %s"
        cursor.execute(query, (user_id,))  # Execute query to fetch teacher ID
        teacher_id = cursor.fetchone()
        cursor.close()
        return teacher_id["teacher_id"] if teacher_id else None  # Return teacher ID or None if not found
    except Exception as e:
        return None  # Handle any exceptions by returning None

# Retrieve parent ID from the database using the user's ID
def get_parent_id(user_id):
    try:
        mysql = get_mysql()  # Get MySQL connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = "SELECT parent_id FROM parents WHERE user_id = %s"
        cursor.execute(query, (user_id,))  # Execute query to fetch parent ID
        parent_id = cursor.fetchone()
        cursor.close()
        return parent_id["parent_id"] if parent_id else None  # Return parent ID or None if not found
    except Exception as e:
        return None  # Handle any exceptions by returning None

# Route to get the role from a JWT token
@decorator_routes.route('/get_role', methods=['POST'])
def role_route():
    jwt_token = request.json.get('token')  # Extract token from request
    if not jwt_token:
        return jsonify({"message": "Token is required"}), 400  # Return error if token is missing
    result = get_role(jwt_token)  # Get role from token
    return jsonify(result)

# Route to get the email from a JWT token
@decorator_routes.route('/get_email', methods=['POST'])
def email_route():
    jwt_token = request.json.get('token')  # Extract token from request
    if not jwt_token:
        return jsonify({"message": "Token is required"}), 400  # Return error if token is missing
    email = get_email(jwt_token)  # Get email from token
    if email:
        return jsonify({"email": email})  # Return email if found
    else:
        return jsonify({"message": "Email not found"}), 404  # Return error if email is not found

# Route to get the user ID from a JWT token
@decorator_routes.route('/get_id', methods=['POST'])
def id_route():
    jwt_token = request.json.get('token')  # Extract token from request
    if not jwt_token:
        return jsonify({"message": "Token is required"}), 400  # Return error if token is missing
    user_id = get_id(jwt_token)  # Get user ID from token
    if isinstance(user_id, dict):  # Check if the response is an error message
        return jsonify(user_id), 401  # Return error if JWT validation failed
    else:
        return jsonify({"user_id": user_id})  # Return user ID if successful
