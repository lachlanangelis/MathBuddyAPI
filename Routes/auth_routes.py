# Import necessary modules and functions from Flask and other libraries
from flask import Blueprint, request, jsonify, current_app
import MySQLdb.cursors
import bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Create a Blueprint for authentication routes
auth_routes = Blueprint('auth_routes', __name__)

# Helper function to get the MySQL connection from the app configuration
def get_mysql():
    return current_app.config['mysql']

# Define the login route
@auth_routes.route('/login', methods=['POST'])
def login():
    try:
        # Get MySQL connection
        mysql = get_mysql()
        # Get the JSON data from the request
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # Check if email and password are provided
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Query the database for the user with the given email
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        # If the user is found, check the password
        if user:
            stored_password = user['password']
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                # Create an access token if the password is correct
                access_token = create_access_token(identity={"email": email, "role": user["role"]})
                return jsonify({"access_token": access_token}), 200
            else:
                return jsonify({"message": "Invalid credentials"}), 401
        else:
            return jsonify({"message": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Define the signup route
#TODO separate teacher and student signup
@auth_routes.route('/signup', methods=['POST'])
def signup():
    try:
        # Get MySQL connection
        mysql = get_mysql()
        # Get the JSON data from the request
        data = request.get_json()
        password = data.get('password')
        email = data.get('email')
        role = data.get('role')

        # Validate the input
        if not password or not email or not role:
            return jsonify({"error": "Missing required fields"}), 400

        # Check if the email already exists in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            return jsonify({"error": "Email already exists"}), 400

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert the new user into the database
        cursor.execute("INSERT INTO users (password, email, role) VALUES (%s, %s, %s)",
                       (hashed_password.decode('utf-8'), email, role))
        mysql.connection.commit()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
