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
from env_var import *

app = Flask(__name__)

app.register_blueprint(quiz_routes)
app.register_blueprint(sql_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(ollama_routes)
app.register_blueprint(student_routes)
app.register_blueprint(teacher_routes)
app.register_blueprint(parent_routes)


app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB

# Configure JWT
app.config['JWT_SECRET_KEY'] = api_key  # Change this to a secure secret key
jwt = JWTManager(app)

mysql = MySQL(app)
app.config['mysql'] =mysql

@app.route('/')
def hello_world():
    # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    #Allows methods from react
    CORS(app)
    app.run()
    
