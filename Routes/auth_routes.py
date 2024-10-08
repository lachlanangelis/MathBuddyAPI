from flask import Blueprint, request, jsonify, current_app
import MySQLdb.cursors
import bcrypt
from flask_jwt_extended import create_access_token

# Create a Blueprint for authentication routes
auth_routes = Blueprint('auth_routes', __name__)

# Helper function to get the MySQL connection from the app configuration
def get_mysql():
    return current_app.config['mysql']


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
        cursor.close()  # Close cursor after use

        # If the user is found, check the password
        if user:
            stored_password = user.get('password')
            if stored_password and bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                # Create an access token if the password is correct
                access_token = create_access_token(identity={
                    "email": email,
                    "role": user.get("role"),
                    "user_id": user.get("user_id")  # Include user_id in the identity
                })

                # Extract the full_name and role from the user data
                full_name = user.get('full_name')
                role = user.get('role')

                # Return the token, full_name, and other user details
                return jsonify({
                    "access_token": access_token,
                    "personObj": {
                        "full_name": full_name,
                        "role": role
                        # Include any other relevant user details here
                    }
                }), 200
            else:
                return jsonify({"message": "Invalid credentials"}), 401
        else:
            return jsonify({"message": "User not found"}), 404

    except Exception as e:
        # Log the exception details for debugging
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred during login. Please try again later."}), 500
    
# Define the signup route
# TODO separate teacher and student signup
@auth_routes.route('/signupTeach', methods=['POST'])
def signup():
    try:
        # Get MySQL connection
        mysql = get_mysql()
        # Get the JSON data from the request
        data = request.get_json()
        password = data.get('password')
        email = data.get('email')
        full_name = data.get('full_name')
        phone = data.get('phone')

        # Validate the input
        if not password or not email:
            return jsonify({"error": "Missing required fields"}), 400

        # Check if the email already exists in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            cursor.close()
            return jsonify({"error": "Email already exists"}), 400

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert the new user into the database
        cursor.execute("INSERT INTO users (password, email, role, full_name, mobile_phone) VALUES (%s, %s, 'teacher', "
                       "%s, %s)",
                       (hashed_password.decode('utf-8'), email, full_name, phone))
        mysql.connection.commit()

        # Retrieve the user_id of the newly inserted user
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        user_record = cursor.fetchone()
        user_id = user_record['user_id'] if user_record else None

        if not user_id:
            cursor.close()
            return jsonify({"error": "Failed to retrieve user ID"}), 500

        # Insert into teachers table
        cursor.execute("INSERT INTO teachers (teacher_name, user_id) VALUES (%s, %s)",
                       (full_name, user_id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_routes.route('/signupStu', methods=['POST'])
def signupStu():
    try:
        # Get MySQL connection
        mysql = get_mysql()
        data = request.get_json()
        password = data.get('password')
        email = data.get('email')
        phone = data.get('phone')
        full_name = data.get('full_name')

        if not password or not email or not phone or not full_name:
            return jsonify({"error": "Missing required fields"}), 400

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "Student email already exists"}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (password, email, role, full_name, mobile_phone) VALUES (%s, %s, 'student', %s, %s)",
            (hashed_password, email, full_name, phone)
        )
        mysql.connection.commit()
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        user_record = cursor.fetchone()
        student_user_id = user_record['user_id'] if user_record else None

        if not student_user_id:
            cursor.close()
            return jsonify({"error": "Failed to retrieve student user ID"}), 500

        cursor.execute("INSERT INTO students (student_name, user_id) VALUES (%s, %s)", (full_name, student_user_id))
        mysql.connection.commit()
        
        # Fetch the student_id from the students table
        cursor.execute("SELECT student_id FROM students WHERE user_id = %s", (student_user_id,))
        student_record = cursor.fetchone()
        student_id = student_record['student_id'] if student_record else None

        if not student_id:
            cursor.close()
            return jsonify({"error": "Failed to retrieve student ID"}), 500

        parent_email = f"{full_name.replace(' ', '').lower()}@parent.com"
        cursor.execute("SELECT * FROM users WHERE email = %s", (parent_email,))
        if cursor.fetchone():
            return jsonify({"error": "Parent email already exists"}), 400

        cursor.execute(
            "INSERT INTO users (password, email, role, full_name) VALUES (%s, %s, 'parent', %s)",
            (hashed_password, parent_email, f"{full_name}'s Parent")
        )
        mysql.connection.commit()

        cursor.execute("SELECT user_id FROM users WHERE email = %s", (parent_email,))
        parent_user_record = cursor.fetchone()
        parent_user_id = parent_user_record['user_id'] if parent_user_record else None

        if not parent_user_id:
            cursor.close()
            return jsonify({"error": "Failed to retrieve parent user ID"}), 500

        # Insert into parents table using the correct student_id
        cursor.execute("INSERT INTO parents (parent_name, user_id, child_id) VALUES (%s, %s, %s)", 
                       (f"{full_name}'s Parent", parent_user_id, student_id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Student and Parent registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# parent signup route
@auth_routes.route('/signupParent', methods=['POST'])
def signup_parent():
    try:
        # Get MySQL connection
        mysql = get_mysql()
        # Get the JSON data from the request
        data = request.get_json()
        password = data.get('password')
        email = data.get('email')
        full_name = data.get('full_name')
        phone = data.get('phone')
        child_id = data.get('child_id')

        # Validate the input
        if not password or not email or not full_name or not phone or not child_id:
            return jsonify({"error": "Missing required fields"}), 400

        # Check if the email already exists in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            cursor.close()
            return jsonify({"error": "Email already exists"}), 400

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert the new user into the database
        cursor.execute("INSERT INTO users (password, email, role, full_name, mobile_phone) VALUES (%s, %s, 'parent', %s, %s)",
                       (hashed_password.decode('utf-8'), email, full_name, phone))
        mysql.connection.commit()

        # Retrieve the user_id of the newly inserted user
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        user_record = cursor.fetchone()
        user_id = user_record['user_id'] if user_record else None

        if not user_id:
            cursor.close()
            return jsonify({"error": "Failed to retrieve user ID"}), 500

        # Insert into parents table
        cursor.execute("INSERT INTO parents (parent_name, user_id, child_id) VALUES (%s, %s, %s)",
                       (full_name, user_id, child_id))
        mysql.connection.commit()

        cursor.close()

        return jsonify({"message": "Parent registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
