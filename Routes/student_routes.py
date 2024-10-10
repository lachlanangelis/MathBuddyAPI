#Authors Lachlan,Zuhayer
import MySQLdb.cursors
from decorator import *

student_routes = Blueprint('student_routes', __name__)

def get_mysql():
    return current_app.config['mysql']

# Route to get students quiz list: includes completions, scores, due date and time limit.
@student_routes.route('/getStudentQuiz', methods=['POST'])
def getStudentQuiz():
    data = request.get_json()
    token = data['token']
    student_id = get_id(token)

    mysql = get_mysql()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Query to get all quizzes for a student
    sql_query = '''
    SELECT 
        s.student_id,
        s.student_name,
        q.quiz_id,
        q.title AS quiz_title,
        q.description AS quiz_description,
        q.due_date,
        q.time_limit,
        sq.score,
        sq.feedback AS student_feedback,
        sq.completed,
        sq.completed_at
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


# Route to get student pending quizzes (not completed)
@student_routes.route('/getStudentPendingQuizzes', methods=['POST'])
def get_student_pending_quizzes():
    if request.method == 'POST':
        data = request.get_json()
        token = data['token']
        student_id = get_id(token)

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Query to get only quizzes that haven't been completed
        sql_query = '''
        SELECT 
            s.student_id,
            s.student_name,
            q.quiz_id,
            q.title AS quiz_title,
            q.description AS quiz_description,
            q.due_date,
            sq.score,
            sq.feedback AS student_feedback
        FROM 
            students s
        JOIN 
            student_quizzes sq ON s.student_id = sq.student_id
        JOIN 
            quizzes q ON sq.quiz_id = q.quiz_id
        WHERE 
            s.student_id = %s AND sq.completed = 0
        '''
        cursor.execute(sql_query, (student_id,))
        pending_quizzes = cursor.fetchall()

        cursor.close()
        return jsonify(pending_quizzes)

# Route to get students current quiz, this should list the questions.
@student_routes.route('/current_quiz', methods=['POST'])
def get_current_quiz():
    try:
        data = request.get_json()
        token = data['token']
        quiz_id = data['quiz_id']

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to get the quiz details and questions
        query = """
        SELECT q.quiz_id, q.time_limit, qq.question_id, qq.question_text, qq.question_number
        FROM quizzes q
        JOIN quiz_questions qq ON q.quiz_id = qq.quiz_id
        WHERE q.quiz_id = %s
        ORDER BY qq.question_number
        """
        cursor.execute(query, (quiz_id,))
        results = cursor.fetchall()
        cursor.close()

        if results:
            # Separate quiz details and questions
            quiz_info = {
                'time_limit': results[0]['time_limit'],
                'questions': []
            }
            for row in results:
                quiz_info['questions'].append({
                    'question_id': row['question_id'],
                    'question_text': row['question_text'],
                    'question_number': row['question_number']
                })
            return jsonify(quiz_info), 200
        else:
            return jsonify({"message": "No questions found for the specified quiz"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to display personal information of students
@student_routes.route('/student', methods=['POST'])
def get_student_by_id():
    try:
        data = request.get_json()
        token = data['token']
        student_id = get_id(token)

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Modified query to join the classes table and get the class name
        query = """
        SELECT 
            s.student_id,
            s.student_name,
            c.class_name,  -- Fetching class name instead of class ID
            u.date_of_birth,
            u.gender,
            u.full_name,
            u.preferred_first_name,
            u.city,
            u.state,
            u.postal_code,
            u.address,
            u.mobile_phone,
            u.home_phone,
            u.email
        FROM 
            students s
        JOIN 
            users u ON s.user_id = u.user_id
        JOIN
            classes c ON s.class_id = c.class_id  -- Join with classes table to get the class name
        WHERE 
            s.student_id = %s
        """
        cursor.execute(query, (student_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"message": "Student not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to modify student data including, Name, Gender, DOB, etc.
@student_routes.route('/update_student_profile', methods=['POST'])
def update_student_profile():
    try:
        data = request.get_json()
        token = data.get('token')
        student_id = get_id(token)
        user_id = get_uid(token)

        if not student_id or not user_id:
            return jsonify({"error": "Missing student_id or user_id parameter"}), 400

        # Get optional fields
        fields = {
            "student_name": data.get('student_name'),
            "date_of_birth": data.get('date_of_birth'),
            "gender": data.get('gender'),
            "full_name": data.get('full_name'),
            "preferred_first_name": data.get('preferred_first_name'),
            "city": data.get('city'),
            "state": data.get('state'),
            "postal_code": data.get('postal_code'),
            "address": data.get('address'),
            "mobile_phone": data.get('mobile_phone'),
            "home_phone": data.get('home_phone'),
            "email": data.get('email'),
            "password": data.get('password')
        }

        # Separate fields for students and users
        update_fields_students = {key: value for key, value in fields.items() if key in ["student_name"] and value}
        update_fields_users = {key: value for key, value in fields.items() if key in ["date_of_birth", "gender", "full_name", "preferred_first_name", "city", "state", "postal_code", "address", "mobile_phone", "home_phone", "email", "password"] and value}

        if not update_fields_students and not update_fields_users:
            return jsonify({"error": "No valid fields provided for update"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Update student information
        if update_fields_students:
            set_clause = ', '.join(f"{key} = %s" for key in update_fields_students)
            update_students_query = f"UPDATE students SET {set_clause} WHERE student_id = %s"
            parameters_students = list(update_fields_students.values()) + [student_id]
            cursor.execute(update_students_query, tuple(parameters_students))

        # Update user information
        if update_fields_users:
            set_clause = ', '.join(f"{key} = %s" for key in update_fields_users)
            update_users_query = f"UPDATE users SET {set_clause} WHERE user_id = %s"
            parameters_users = list(update_fields_users.values()) + [user_id]
            cursor.execute(update_users_query, tuple(parameters_users))

        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Student profile updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get student feedback for a specific quiz
@student_routes.route('/student/<int:student_id>/quiz_results/<int:quiz_id>', methods=['GET'])
def get_quiz_result_for_specific_quiz(student_id, quiz_id):
    try:
        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to get the quiz result for a specific quiz from the student_quizzes table
        query = """
        SELECT 
            sq.quiz_id,
            q.title AS quiz_title,
            sq.score,
            sq.additional_feedback_teacher,
            sq.feedback AS feedback_text_ai
        FROM 
            student_quizzes sq
        JOIN 
            quizzes q ON sq.quiz_id = q.quiz_id
        WHERE 
            sq.student_id = %s AND sq.quiz_id = %s
        """
        cursor.execute(query, (student_id, quiz_id))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"message": "No quiz result found for this quiz and student"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get student classes
@student_routes.route('/student/<int:student_id>/classes', methods=['GET'])
def get_student_classes(student_id):
    try:
        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to get the class information for the student
        query = """
        SELECT 
            c.class_id,
            c.class_name,
            c.teacher_id,
            t.teacher_name
        FROM 
            classes c
        JOIN 
            students s ON s.class_id = c.class_id
        JOIN 
            teachers t ON c.teacher_id = t.teacher_id
        WHERE 
            s.student_id = %s
        """
        cursor.execute(query, (student_id,))
        class_info = cursor.fetchone()
        cursor.close()

        if class_info:
            return jsonify(class_info), 200
        else:
            return jsonify({"message": "Class information not found for this student"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get student lessons
@student_routes.route('/student/<int:student_id>/lessons', methods=['GET'])
def get_student_lessons(student_id):
    try:
        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to get the lessons for the student's class
        query = """
        SELECT 
            l.lesson_id,
            l.teacher_id,
            l.class_id,
            l.title AS lesson_title,
            l.content AS lesson_content
        FROM 
            lessons l
        JOIN 
            students s ON s.class_id = l.class_id
        WHERE 
            s.student_id = %s
        """
        cursor.execute(query, (student_id,))
        lessons = cursor.fetchall()
        cursor.close()

        if lessons:
            return jsonify(lessons), 200
        else:
            return jsonify({"message": "No lessons found for this student"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to quiz completion message
@student_routes.route('/student/<int:student_id>/quiz/<int:quiz_id>/complete', methods=['POST'])
def complete_quiz(student_id, quiz_id):
    try:
        # Get MySQL connection
        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check if the quiz has already been completed
        cursor.execute("""
            SELECT completed FROM student_quizzes 
            WHERE student_id = %s AND quiz_id = %s
        """, (student_id, quiz_id))
        quiz = cursor.fetchone()

        if not quiz:
            return jsonify({"error": "Quiz not found for this student"}), 404
        
        if quiz['completed'] == 1:
            # Return a completion message
            return jsonify({"message": "Quiz has been successfully completed!"}), 200
        else:
            return jsonify({"message": "Quiz is not yet completed."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@student_routes.route('/getStudentCompletedQuizzes', methods=['POST'])
def get_student_completed_quizzes():
    if request.method == 'POST':
        data = request.get_json()
        token = data['token']
        student_id = get_id(token)

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to get only quizzes that have been completed
        sql_query = '''
        SELECT 
            s.student_id,
            s.student_name,
            q.quiz_id,
            q.title AS quiz_title,
            q.description AS quiz_description,
            sq.completed_at,
            sq.score,
            sq.feedback AS student_feedback
        FROM 
            students s
        JOIN 
            student_quizzes sq ON s.student_id = sq.student_id
        JOIN 
            quizzes q ON sq.quiz_id = q.quiz_id
        WHERE 
            s.student_id = %s AND sq.completed = 1
        '''
        cursor.execute(sql_query, (student_id,))
        completed_quizzes = cursor.fetchall()

        cursor.close()
        return jsonify(completed_quizzes)


# Route to display active homework with quiz title and due date

@student_routes.route('/get_student_grade', methods=['POST'])
def get_student_grade():
    try:
        data = request.get_json()
        token = data['token']
        student_id = get_id(token)
        
        # Get MySQL connection
        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Query to get the student's grade from the classes table
        cursor.execute("""
            SELECT c.class_grade
            FROM students s
            JOIN classes c ON s.class_id = c.class_id
            WHERE s.student_id = %s
        """, (student_id,))
        
        grade_result = cursor.fetchone()
        
        if not grade_result:
            return jsonify({"error": "Grade not found for this student"}), 404

        # Close the cursor
        cursor.close()
        
        return jsonify({"grade": grade_result['class_grade']}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500