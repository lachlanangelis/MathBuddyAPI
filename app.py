#Authors Lachlan,Zuhayer, Raul
from flask_jwt_extended import JWTManager
from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS

from Routes.student_routes import student_routes
from Routes.quiz_routes import quiz_routes
from Routes.sql_routes import sql_routes
from Routes.auth_routes import auth_routes
from Routes.ollama_routes import ollama_routes
from Routes.teacher_routes import teacher_routes
from Routes.parent_routes import parent_routes
from Routes.Lresources import Lresources
from decorator import decorator_routes
from env_var import *

def create_app():
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(quiz_routes)
    app.register_blueprint(sql_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(ollama_routes)
    app.register_blueprint(student_routes)
    app.register_blueprint(teacher_routes)
    app.register_blueprint(parent_routes)
    app.register_blueprint(decorator_routes)
    app.register_blueprint(Lresources)

    # Configure MySQL
    app.config['MYSQL_HOST'] = MYSQL_HOST
    app.config['MYSQL_USER'] = MYSQL_USER
    app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
    app.config['MYSQL_DB'] = MYSQL_DB
    mysql = MySQL(app)
    app.config['mysql'] = mysql

    # Configure JWT
    app.config['JWT_SECRET_KEY'] = api_key  # Change this to a secure secret key
    jwt = JWTManager(app)

    # Enable CORS
    CORS(app)

    # Add routes
    @app.route('/')
    def hello_world():
        return 'Hello World!'

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
