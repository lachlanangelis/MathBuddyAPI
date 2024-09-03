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
@student_routes.route('/student/<int:student_id>/current_quiz', methods=['GET'])
def get_current_quiz(student_id):
    try:
        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to get the current quiz assigned to the student's class
        query = """
        SELECT 
            q.quiz_id,
            q.title AS quiz_title,
            q.description AS quiz_description,
            qq.question_id,
            qq.question_text
        FROM 
            quizzes q
        JOIN 
            quiz_questions qq ON q.quiz_id = qq.quiz_id
        JOIN 
            student_quizzes sq ON sq.quiz_id = q.quiz_id
        JOIN 
            students s ON s.student_id = sq.student_id
        WHERE 
            s.student_id = %s AND sq.completed = 0
        """
        cursor.execute(query, (student_id,))
        quizzes = cursor.fetchall()
        cursor.close()

        if quizzes:
            return jsonify(quizzes), 200
        else:
            return jsonify({"message": "No current quiz found for this student"}), 404

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

        # Query to get the student's personal information
        query = """
        SELECT 
            s.student_id,
            s.student_name,
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
        token = data['token']
        student_id = get_student_id(token)

        # Optional fields that can be updated
        student_name = data.get('student_name')
        date_of_birth = data.get('date_of_birth')
        gender = data.get('gender')
        full_name = data.get('full_name')
        preferred_first_name = data.get('preferred_first_name')
        city = data.get('city')
        state = data.get('state')
        postal_code = data.get('postal_code')
        address = data.get('address')
        mobile_phone = data.get('mobile_phone')
        home_phone = data.get('home_phone')
        email = data.get('email')
        password = data.get('password')

        if not student_id:
            return jsonify({"error": "Missing student_id parameter"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        update_fields_students = []
        update_fields_users = []
        parameters_students = []
        parameters_users = []

        if student_name:
            update_fields_students.append("student_name = %s")
            parameters_students.append(student_name)

        if date_of_birth:
            update_fields_users.append("date_of_birth = %s")
            parameters_users.append(date_of_birth)

        if gender:
            update_fields_users.append("gender = %s")
            parameters_users.append(gender)

        if full_name:
            update_fields_users.append("full_name = %s")
            parameters_users.append(full_name)

        if preferred_first_name:
            update_fields_users.append("preferred_first_name = %s")
            parameters_users.append(preferred_first_name)

        if city:
            update_fields_users.append("city = %s")
            parameters_users.append(city)

        if state:
            update_fields_users.append("state = %s")
            parameters_users.append(state)

        if postal_code:
            update_fields_users.append("postal_code = %s")
            parameters_users.append(postal_code)

        if address:
            update_fields_users.append("address = %s")
            parameters_users.append(address)

        if mobile_phone:
            update_fields_users.append("mobile_phone = %s")
            parameters_users.append(mobile_phone)

        if home_phone:
            update_fields_users.append("home_phone = %s")
            parameters_users.append(home_phone)

        if email:
            update_fields_users.append("email = %s")
            parameters_users.append(email)

        if password:
            update_fields_users.append("password = %s")
            parameters_users.append(password)

        if not update_fields_students and not update_fields_users:
            return jsonify({"error": "No valid fields provided for update"}), 400

        if update_fields_students:
            update_students_query = f"""
            UPDATE students
            SET {', '.join(update_fields_students)}
            WHERE student_id = %s
            """
            parameters_students.append(student_id)
            cursor.execute(update_students_query, tuple(parameters_students))

        if update_fields_users:
            cursor.execute("""
                SELECT user_id FROM students WHERE student_id = %s
            """, (student_id,))
            user = cursor.fetchone()

            if user:
                update_users_query = f"""
                UPDATE users
                SET {', '.join(update_fields_users)}
                WHERE user_id = %s
                """
                parameters_users.append(user['user_id'])
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

# Route to save a quiz, this includes marking the quiz, sending the prompt for AI feedback, and storing the result.
# @student_routes.route('/submit_quiz', methods=['POST'])
# still need ai functions to mark and give feedback!

# Route to display active homework with quiz title and due date
