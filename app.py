from flask_jwt_extended import JWTManager
from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS

# Importing blueprints (modular routes) from different parts of the application
from Routes.student_routes import student_routes
from Routes.quiz_routes import quiz_routes
from Routes.sql_routes import sql_routes
from Routes.auth_routes import auth_routes
from Routes.ollama_routes import ollama_routes
from Routes.teacher_routes import teacher_routes
from Routes.parent_routes import parent_routes
from Routes.Lresources import Lresources
from decorator import decorator_routes

# Import environment variables for database and security
from env_var import *

# Initialize the Flask app
app = Flask(__name__)

# Register all blueprints (separate route modules)
app.register_blueprint(quiz_routes)
app.register_blueprint(sql_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(ollama_routes)
app.register_blueprint(student_routes)
app.register_blueprint(teacher_routes)
app.register_blueprint(parent_routes)
app.register_blueprint(decorator_routes)
app.register_blueprint(Lresources)

# MySQL configuration from environment variables
app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB

# Initialize MySQL connection
mysql = MySQL(app)
app.config['mysql'] = mysql  # Store MySQL object in app config

# JWT (JSON Web Token) configuration for authentication
app.config['JWT_SECRET_KEY'] = api_key  # Ensure to use a secure, random secret key
jwt = JWTManager(app)  # Initialize JWT manager

# A basic route for testing if the server is running
@app.route('/')
def hello_world():
    return 'Hello World!'  # Returns a simple message when accessing the root URL

# Start the Flask application
if __name__ == '__main__':
    # Enable CORS (Cross-Origin Resource Sharing) to allow requests from different origins (e.g., from React frontend)
    CORS(app)
    # Run the application
    app.run()
