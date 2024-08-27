from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
import jwt
import MySQLdb.cursors
from app import mysql
from env_var import *


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


def get_role(jwt_token):
    try:
        # Decode the JWT token using the PyJWT library
        decoded_token = jwt.decode(jwt_token, api_key, algorithms=["HS256"])

        # Extract the identity (which contains email and role)
        identity = decoded_token.get('sub')

        if identity:
            role = identity.get('role')
            email = identity.get('email')
            print(role)
            return {"role": role, "email": email}
        else:
            return None
    except jwt.ExpiredSignatureError:
        return {"message": "Token expired"}, 401
    except jwt.InvalidTokenError:
        return {"message": "Invalid token"}, 401
    except Exception as e:
        return {"message": str(e)}, 401


def get_email(jwt_token):
    try:
        # Decode the JWT token using the PyJWT library
        decoded_token = jwt.decode(jwt_token, api_key, algorithms=["HS256"])

        # Extract the identity (which contains email and role)
        identity = decoded_token.get('sub')

        if identity:
            email = identity.get('email')
            return email
        else:
            return None
    except jwt.ExpiredSignatureError:
        return {"message": "Token expired"}, 401
    except jwt.InvalidTokenError:
        return {"message": "Invalid token"}, 401
    except Exception as e:
        return {"message": str(e)}, 401


def get_id(jwt_token):
    try:
        # Decode the JWT token using the PyJWT library
        decoded_token = jwt.decode(jwt_token, api_key, algorithms=["HS256"])

        # Extract the identity (which contains email, role, and user_id)
        identity = decoded_token.get('identity', {})

        if identity:
            role = identity.get('role')
            user_id = identity.get('user_id')

            if role == 'student':
                # Assuming you have a function `get_student_id` to retrieve student_id
                student_id = get_student_id(user_id)
                return student_id

            elif role == 'teacher':
                # Assuming you have a function `get_teacher_id` to retrieve teacher_id
                teacher_id = get_teacher_id(user_id)
                return teacher_id

            elif role == 'parent':
                # Assuming you have a function `get_parent_id` to retrieve parent_id
                parent_id = get_parent_id(user_id)
                return parent_id

            else:
                raise ValueError("Unknown role")

        else:
            raise ValueError("Invalid token")

    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}, 401
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}, 401
    except Exception as e:
        return {"error": str(e)}, 500


def get_student_id(user_id):
    # Implement this function to retrieve student_id based on user_id
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = "SELECT student_id FROM students WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    stu_id = cursor.fetchone()

    cursor.close()  # It's a good practice to close the cursor when done
    return stu_id

def get_teacher_id(user_id):
    # Implement this function to retrieve teacher_id based on user_id
    # This is a placeholder
    pass


def get_parent_id(user_id):
    # Implement this function to retrieve parent_id based on user_id
    # This is a placeholder
    pass


get_id("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyNDcxOTQyOSwianRpIjoiMjgwNmQ4YTktZWQ2Yi00NWE4LWE0YjktYzUyOWMyNzEzZWFlIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJlbWFpbCI6ImJydWhAZXhhbXBsZS5jb20iLCJyb2xlIjoic3R1ZGVudCJ9LCJuYmYiOjE3MjQ3MTk0MjksImNzcmYiOiI1YTg4OTA0NC1hNmZiLTQ2ZjItYjNjNi02ZDg2ODg0YjczNzUiLCJleHAiOjE3MjQ3MjAzMjl9.Jy95z16HPIkYxy7EJn0Je_FOJkjkYO_W6gpuAsfreNY")
