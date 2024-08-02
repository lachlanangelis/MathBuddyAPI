# app/routes/auth.py
import MySQLdb.cursors
import bcrypt
from flask import Blueprint, request, jsonify, current_app

auth_routes = Blueprint('auth_routes', __name__)

def get_mysql():
    return current_app.config['mysql']

@auth_routes.route('/login', methods=['POST'])
def login():
    try:
        mysql = get_mysql()
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            stored_password = user['password']
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                return jsonify({"message": "Login successful"}), 200
            else:
                return jsonify({"message": "Invalid credentials"}), 401
        else:
            return jsonify({"message": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_routes.route('/signup', methods=['POST'])
def signup():
    try:
        mysql = get_mysql()
        data = request.get_json()
        password = data.get('password')
        email = data.get('email')
        role = data.get('role')

        # Validate the input
        if not password or not email or not role:
            return jsonify({"error": "Missing required fields"}), 400

        # Check if the email already exists
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
