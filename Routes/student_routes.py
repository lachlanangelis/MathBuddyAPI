import MySQLdb.cursors
from flask import Blueprint, jsonify, current_app

student_routes = Blueprint('student_routes', __name__)

def get_mysql():
    return current_app.config['mysql']

#TODO endpoint to display quizzes and status

#TODO endpoint to display lessons

#TODO endpoint to display feedback

#TODO endpoint to display student personal information

#TODO function to edit personal info and update db

#TODO function to display quiz questions 

#TODO function to take quiz answers, grade it and store in db
