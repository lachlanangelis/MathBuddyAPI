import MySQLdb.cursors
from flask_mysqldb import MySQL
from flask import Blueprint, jsonify, current_app, Response, request

student_routes = Blueprint('student_routes', __name__)

def get_mysql():
    return current_app.config['mysql']

# Route to get students quiz list: includes completions, scores, due date and time limit.
@student_routes.route('/getStudentQuiz', methods=['POST'])
def getStudentQuiz():
    if request.method == 'POST':
        data = request.get_json()
        student_id = data['student_id']

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Place query here
        sql_query = '''
        SELECT 
            s.student_id,
            s.student_name,
            q.quiz_id,
            sq.score,
            sq.feedback AS student_feedback
        FROM 
            students s
        JOIN 
            student_quizzes sq ON s.student_id = sq.student_id
        JOIN 
            quizzes q ON sq.quiz_id = q.quiz_id
        WHERE 
            s.student_id = %s
        '''
        cursor.execute(sql_query, (student_id,))
        quizzes = cursor.fetchall()

        cursor.close()
        return jsonify(quizzes)

# Route to get students current quiz, this should list the questions.

# Route to save a quiz, this includes marking the quiz, sending the prompt for ai feedback storing the result.

# Route to modify student data including, Name, Gender, DOB.

# Route to get student feedback, this should have the quizz name and the result/feedback associated
