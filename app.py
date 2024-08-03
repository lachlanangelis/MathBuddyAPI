from flask_jwt_extended import JWTManager
from flask import Flask
from flask_mysqldb import MySQL
from Routes.quiz_routes import quiz_routes
from Routes.sql_routes import sql_routes
from Routes.auth_routes import auth_routes
from Routes.ollama_routes import ollama_routes
from env_var import *

app = Flask(__name__)

app.register_blueprint(quiz_routes)
app.register_blueprint(sql_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(ollama_routes)

app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB

# Configure JWT
app.config['JWT_SECRET_KEY'] = api_key  # Change this to a secure secret key
jwt = JWTManager(app)

mysql = MySQL(app)

@app.route('/')
def hello_world():
    # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
