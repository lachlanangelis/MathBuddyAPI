import MySQLdb.cursors
from flask import Blueprint, jsonify, current_app

parent_routes = Blueprint('parent_routes', __name__)

def get_mysql():
    return current_app.config['mysql']

#Route to display the child information of the parent

#Route to display pending tasks of the child 

#Route to display Progress report

#Route to display Child feedback

#Route to display parent information

#Route to edit parent information

