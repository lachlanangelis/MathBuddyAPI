import MySQLdb.cursors
from flask import Blueprint, jsonify, current_app

student_routes = Blueprint('student_routes', __name__)

# Route to get students quiz list: includes completions, scores, ai feedback.

# Route to get students current quiz, this should list the questions. 

# Route to save a quiz, this includes marking the quiz, sending the prompt for ai feedback storing the result.

# Route to modify student data including, Name, Gender, DOB.

# Route to get student feedback, this should have the quizz name and the result/feedback associated

@student_routes.route()