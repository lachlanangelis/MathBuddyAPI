import MySQLdb.cursors
from flask import Blueprint, jsonify, current_app

sql_routes = Blueprint('sql_routes', __name__)

def get_mysql():
    return current_app.config['mysql']

# Database Query functions and routes
def fetch_data_from_table(table_name):
    mysql = get_mysql()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    cur.close()
    return rows

@sql_routes.route('/tables', methods=['GET'])
def get_tables():
    mysql = get_mysql()
    cur = mysql.connection.cursor()
    cur.execute("SHOW TABLES")
    tables = cur.fetchall()
    table_list = [table[0] for table in tables]
    cur.close()
    return jsonify(table_list)

@sql_routes.route('/tables/<table_name>', methods=['GET'])
def get_table_data(table_name):
    try:
        data = fetch_data_from_table(table_name)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@sql_routes.route('/classes', methods=['GET'])
def get_classes():
    data = fetch_data_from_table('classes')
    return jsonify(data)

@sql_routes.route('/feedback', methods=['GET'])
def get_feedback():
    data = fetch_data_from_table('feedback')
    return jsonify(data)

@sql_routes.route('/lessons', methods=['GET'])
def get_lessons():
    data = fetch_data_from_table('lessons')
    return jsonify(data)

@sql_routes.route('/parents', methods=['GET'])
def get_parents():
    data = fetch_data_from_table('parents')
    return jsonify(data)

@sql_routes.route('/quizzes', methods=['GET'])
def get_quizzes():
    data = fetch_data_from_table('quizzes')
    return jsonify(data)

@sql_routes.route('/quiz_questions', methods=['GET'])
def get_quiz_questions():
    data = fetch_data_from_table('quiz_questions')
    return jsonify(data)

@sql_routes.route('/students', methods=['GET'])
def get_students():
    data = fetch_data_from_table('students')
    return jsonify(data)

@sql_routes.route('/student_quizzes', methods=['GET'])
def get_student_quizzes():
    data = fetch_data_from_table('student_quizzes')
    return jsonify(data)

@sql_routes.route('/teachers', methods=['GET'])
def get_teachers():
    data = fetch_data_from_table('teachers')
    return jsonify(data)

@sql_routes.route('/users', methods=['GET'])
def get_users():
    data = fetch_data_from_table('users')
    return jsonify(data)
