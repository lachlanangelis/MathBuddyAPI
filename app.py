from flask_jwt_extended import JWTManager
from flask import Flask
from flask_mysqldb import MySQL
from Routes.quiz_routes import quiz_routes
from Routes.sql_routes import sql_routes
from Routes.auth_routes import auth_routes
from Routes.ollama_routes import ollama_routes

app = Flask(__name__)

app.register_blueprint(quiz_routes)
app.register_blueprint(sql_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(ollama_routes)

app.config['MYSQL_HOST'] = 'mathbuddy.ctm8ysykaehl.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'mathbuddy123'
app.config['MYSQL_DB'] = 'mathbuddy'

# Configure JWT
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a secure secret key
jwt = JWTManager(app)

mysql = MySQL(app)

@app.route('/')
def hello_world():
    # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
