import MySQLdb.cursors
from flask import Blueprint, jsonify, current_app, request

# Create a Blueprint for SQL-related routes
sql_routes = Blueprint('sql_routes', __name__)


# Helper function to get MySQL connection from the Flask app config
def get_mysql():
    return current_app.config['mysql']


# Helper function to fetch all data from a given table
def fetch_data_from_table(table_name):
    mysql = get_mysql()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Execute query to fetch all rows from the specified table
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    cur.close()

    return rows


# Route to get a list of all tables in the database
@sql_routes.route('/tables', methods=['GET'])
def get_tables():
    mysql = get_mysql()
    cur = mysql.connection.cursor()

    # Fetch the list of all tables in the database
    cur.execute("SHOW TABLES")
    tables = cur.fetchall()

    # Convert the results into a list of table names
    table_list = [table[0] for table in tables]
    cur.close()

    return jsonify(table_list)


# Route to fetch all data from a specific table
@sql_routes.route('/tables/<table_name>', methods=['GET'])
def get_table_data(table_name):
    try:
        # Fetch and return data from the specified table
        data = fetch_data_from_table(table_name)
        return jsonify(data)
    except Exception as e:
        # Return an error message if something goes wrong
        return jsonify({"error": str(e)}), 400


# Route to fetch all data from the 'classes' table
@sql_routes.route('/classes', methods=['GET'])
def get_classes():
    data = fetch_data_from_table('classes')
    return jsonify(data)


# Route to fetch all data from the 'feedback' table
@sql_routes.route('/feedback', methods=['GET'])
def get_feedback():
    data = fetch_data_from_table('feedback')
    return jsonify(data)


# Route to fetch all data from the 'lessons' table
@sql_routes.route('/lessons', methods=['GET'])
def get_lessons():
    data = fetch_data_from_table('lessons')
    return jsonify(data)


# Route to fetch all data from the 'parents' table
@sql_routes.route('/parents', methods=['GET'])
def get_parents():
    data = fetch_data_from_table('parents')
    return jsonify(data)


# Route to fetch all data from the 'quizzes' table
@sql_routes.route('/quizzes', methods=['GET'])
def get_quizzes():
    data = fetch_data_from_table('quizzes')
    return jsonify(data)


# Route to fetch all data from the 'quiz_questions' table
@sql_routes.route('/quiz_questions', methods=['GET'])
def get_quiz_questions():
    data = fetch_data_from_table('quiz_questions')
    return jsonify(data)


# Route to fetch all data from the 'students' table
@sql_routes.route('/students', methods=['GET'])
def get_students():
    data = fetch_data_from_table('students')
    return jsonify(data)


# Route to fetch all data from the 'student_quizzes' table
@sql_routes.route('/student_quizzes', methods=['GET'])
def get_student_quizzes():
    data = fetch_data_from_table('student_quizzes')
    return jsonify(data)


# Route to fetch all data from the 'teachers' table
@sql_routes.route('/teachers', methods=['GET'])
def get_teachers():
    data = fetch_data_from_table('teachers')
    return jsonify(data)


# Route to fetch all data from the 'users' table
@sql_routes.route('/users', methods=['GET'])
def get_users():
    data = fetch_data_from_table('users')
    return jsonify(data)
