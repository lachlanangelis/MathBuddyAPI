import MySQLdb.cursors
from flask import Blueprint, jsonify, current_app

student_routes = Blueprint('student_routes', __name__)

@student_routes.route()