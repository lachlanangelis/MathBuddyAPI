import MySQLdb.cursors
from flask import Blueprint, jsonify, current_app

parent_routes = Blueprint('parent_routes', __name__)

def get_mysql():
    return current_app.config['mysql']

