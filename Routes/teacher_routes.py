import MySQLdb.cursors
from flask import Blueprint, jsonify, current_app

teacher_routes = Blueprint('teacher_routes', __name__)

def get_mysql():
    return current_app.config['mysql']


#TODO endpoint to display the classes the teacher teaches

#TODO add a function to create a class and store it in db
 
#TODO endpoint to display feedback for each class quiz

#TODO endpoint to display lessons 

#TODO endpoint to display personal information of teachers

#TODO add function to Edit personal information of teachers
