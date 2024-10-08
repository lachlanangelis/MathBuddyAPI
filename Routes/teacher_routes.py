import MySQLdb.cursors
from decorator import *

# Create a Blueprint for teacher-related routes
teacher_routes = Blueprint('teacher_routes', __name__)

# Helper function to get MySQL connection
def get_mysql():
    return current_app.config['mysql']

# Route to get the list of classes a teacher teaches, including student count
@teacher_routes.route('/teacher_classes', methods=['POST'])
def get_teacher_classes():
    try:
        data = request.get_json()
        token = data['token']
        teacher_id = get_id(token)

        if not teacher_id:
            return jsonify({"error": "Missing teacher_id parameter"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to fetch the classes taught by the teacher along with the student count
        query = """
        SELECT 
            c.class_id,
            c.class_name,
            t.teacher_name,
            COUNT(s.student_id) AS student_count
        FROM 
            classes c
        JOIN 
            teachers t ON c.teacher_id = t.teacher_id
        LEFT JOIN 
            students s ON c.class_id = s.class_id
        WHERE 
            c.teacher_id = %s
        GROUP BY 
            c.class_id, c.class_name, t.teacher_name
        """
        cursor.execute(query, (teacher_id,))
        result = cursor.fetchall()
        cursor.close()

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"message": "No classes found for the given teacher_id"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to create a new class and assign it to a teacher
@teacher_routes.route('/create_class', methods=['POST'])
def create_class():
    try:
        data = request.get_json()
        class_name = data.get('class_name')
        class_grade = data.get('class_grade')
        token = data.get('token')
        teacher_id = get_id(token)

        if not class_name or not teacher_id:
            return jsonify({"error": "Missing class_name or teacher_id"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor()

        # Query to insert a new class
        query = "INSERT INTO classes (class_name, teacher_id, class_grade) VALUES (%s, %s, %s)"
        cursor.execute(query, (class_name, teacher_id, class_grade))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Class created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to update students' class by assigning them to a new class
@teacher_routes.route('/update_students_class', methods=['POST'])
def update_students_class():
    try:
        data = request.json
        student_ids = data.get('student_ids')
        new_class_id = data.get('new_class_id')

        if not student_ids or not new_class_id:
            return jsonify({"error": "Missing student_ids or new_class_id"}), 400

        if not isinstance(student_ids, list):
            return jsonify({"error": "student_ids must be a list"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor()

        # Query to update the class_id for each student
        query = "UPDATE students SET class_id = %s WHERE student_id = %s"
        for student_id in student_ids:
            cursor.execute(query, (new_class_id, student_id))

        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Added students to class successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to display feedback for a specific class and quiz
@teacher_routes.route('/class_feedback', methods=['GET'])
def get_class_feedback():
    try:
        class_id = request.args.get('class_id')
        quiz_id = request.args.get('quiz_id')

        if not class_id or not quiz_id:
            return jsonify({"error": "Missing class_id or quiz_id parameter"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to fetch feedback for students in the class for a specific quiz
        query = """
        SELECT 
            s.student_name,
            sq.score,
            sq.feedback AS feedback_text_ai,
            sq.additional_feedback_teacher
        FROM 
            students s
        JOIN 
            student_quizzes sq ON s.student_id = sq.student_id
        JOIN 
            classes c ON s.class_id = c.class_id
        WHERE 
            sq.quiz_id = %s AND c.class_id = %s;
        """
        cursor.execute(query, (quiz_id, class_id))
        result = cursor.fetchall()
        cursor.close()

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"message": "No feedback found for the given class_id and quiz_id"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to display the lessons taught by the teacher
@teacher_routes.route('/teacher_lessons', methods=['POST'])
def get_teacher_lessons():
    try:
        data = request.get_json()
        token = data['token']
        teacher_id = get_id(token)

        if not teacher_id:
            return jsonify({"error": "Missing teacher_id parameter"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to fetch lessons taught by the teacher
        query = """
        SELECT 
            l.lesson_id,
            l.title,
            l.content,
            c.class_name
        FROM 
            lessons l
        JOIN 
            classes c ON l.class_id = c.class_id
        WHERE 
            l.teacher_id = %s
        """
        cursor.execute(query, (teacher_id,))
        result = cursor.fetchall()
        cursor.close()

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"message": "No lessons found for the given teacher_id"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get personal information of a teacher
@teacher_routes.route('/teacherInfo', methods=['POST'])
def get_teacher_by_id():
    try:
        data = request.get_json()
        token = data['token']
        teacher_id = get_id(token)

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to fetch personal information of the teacher
        query = """
        SELECT 
            t.teacher_id,
            t.teacher_name,
            t.user_id,
            u.date_of_birth,
            u.email,
            u.gender,
            u.full_name,
            u.preferred_first_name,
            u.city,
            u.state,
            u.postal_code,
            u.address,
            u.mobile_phone,
            u.home_phone
        FROM 
            teachers t
        JOIN 
            users u ON t.user_id = u.user_id
        WHERE 
            t.teacher_id = %s
        """
        cursor.execute(query, (teacher_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"message": "Teacher not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to update teacher's personal information
@teacher_routes.route('/update_teacher_profile', methods=['POST'])
def update_teacher_profile():
    try:
        data = request.get_json()
        token = data['token']
        teacher_id = get_id(token)

        # Optional fields that can be updated
        update_fields = {
            "teacher_name": data.get('teacher_name'),
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

        # Ensure there is at least one field to update
        if not any(update_fields.values()):
            return jsonify({"error": "No valid fields provided for update"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Build and execute the update query for the teacher
        set_clause = ', '.join(f"u.{key} = %s" for key, value in update_fields.items() if value)
        update_query = f"""
        UPDATE teachers t
        JOIN users u ON t.user_id = u.user_id
        SET {set_clause}
        WHERE t.teacher_id = %s
        """
        parameters = [value for value in update_fields.values() if value] + [teacher_id]
        cursor.execute(update_query, tuple(parameters))

        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Teacher profile updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to add additional feedback on student quizzes
@teacher_routes.route('/add_additional_feedback', methods=['POST'])
def add_additional_feedback():
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        quiz_id = data.get('quiz_id')
        additional_feedback_teacher = data.get('additional_feedback_teacher')

        if not student_id or not quiz_id or additional_feedback_teacher is None:
            return jsonify({"error": "Missing required parameters"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check if feedback exists for the student and quiz
        cursor.execute("""
            SELECT feedback_id FROM feedback
            WHERE student_id = %s AND quiz_id = %s
        """, (student_id, quiz_id))
        feedback = cursor.fetchone()

        if feedback:
            # Update existing feedback
            cursor.execute("""
            UPDATE feedback
            SET additional_feedback_teacher = %s
            WHERE feedback_id = %s
            """, (additional_feedback_teacher, feedback['feedback_id']))
        else:
            # Insert new feedback
            cursor.execute("""
            INSERT INTO feedback (student_id, quiz_id, additional_feedback_teacher)
            VALUES (%s, %s, %s)
            """, (student_id, quiz_id, additional_feedback_teacher))

        # Update feedback in the student_quizzes table
        cursor.execute("""
            UPDATE student_quizzes
            SET feedback = %s
            WHERE student_id = %s AND quiz_id = %s
        """, (additional_feedback_teacher, student_id, quiz_id))

        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Additional feedback updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to assign a quiz to a specific class
@teacher_routes.route('/assign_quiz', methods=['POST'])
def assign_quiz_to_class():
    try:
        data = request.get_json()
        class_id = data.get('class_id')
        quiz_id = data.get('quiz_id')

        if not class_id or not quiz_id:
            return jsonify({"error": "Both class_id and quiz_id must be provided"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Assign the quiz to the class and create records for each student
        cursor.execute("UPDATE quizzes SET class_id = %s WHERE quiz_id = %s", (class_id, quiz_id))
        cursor.execute("SELECT student_id FROM students WHERE class_id = %s", (class_id,))
        students = cursor.fetchall()

        for student in students:
            cursor.execute("INSERT INTO student_quizzes (student_id, quiz_id) VALUES (%s, %s)", (student['student_id'], quiz_id))

        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Quiz assigned to class and records created for each student successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to view class details and students
@teacher_routes.route('/class_view', methods=['POST'])
def class_view():
    try:
        data = request.get_json()
        token = data['token']
        class_id = data.get('class_id')
        teacher_id = get_id(token)

        if not teacher_id or not class_id:
            return jsonify({"error": "Missing teacher_id or class_id"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to fetch class details
        class_query = """
        SELECT c.class_id, c.class_name, c.class_grade, t.teacher_name
        FROM classes c
        JOIN teachers t ON c.teacher_id = t.teacher_id
        WHERE c.class_id = %s AND c.teacher_id = %s
        """
        cursor.execute(class_query, (class_id, teacher_id))
        class_details = cursor.fetchone()

        if not class_details:
            return jsonify({"error": "Class not found or you don't have permission to view it"}), 404

        # Query to fetch students in the class with their average quiz scores
        students_query = """
        SELECT 
            s.student_id, 
            s.student_name, 
            u.email,
            AVG(sq.score) AS average_mark
        FROM 
            students s
        JOIN 
            users u ON s.user_id = u.user_id
        LEFT JOIN 
            student_quizzes sq ON s.student_id = sq.student_id
        WHERE 
            s.class_id = %s
        GROUP BY 
            s.student_id, s.student_name, u.email
        """
        cursor.execute(students_query, (class_id,))
        students = cursor.fetchall()

        # Handle cases where a student hasn't taken any quizzes
        for student in students:
            student['average_mark'] = student['average_mark'] if student['average_mark'] is not None else 'No quizzes taken'

        cursor.close()

        return jsonify({"class": class_details, "students": students}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to add a student to a class by email
@teacher_routes.route('/addStudent', methods=['POST'])
def add_student_to_class():
    try:
        data = request.get_json()
        student_email = data.get('student_email')
        new_class_id = data.get('new_class_id')

        if not student_email or not new_class_id:
            return jsonify({"error": "Missing student_email or new_class_id"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor()

        # Find the user ID by email
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (student_email,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            return jsonify({"error": "Student with the provided email not found"}), 404

        user_id = result[0]

        # Update the class ID for the student
        cursor.execute("UPDATE students SET class_id = %s WHERE user_id = %s", (new_class_id, user_id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Student's class updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get quizzes assigned by the teacher and their completion status
@teacher_routes.route('/getTeachQuiz', methods=['POST'])
def getTeachQuiz():
    try:
        data = request.get_json()
        token = data['token']
        teacher_id = get_id(token)

        if not teacher_id:
            return jsonify({"error": "Missing teacher_id parameter"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to fetch all class IDs and names taught by the teacher
        class_query = """
        SELECT class_id, class_name
        FROM classes
        WHERE teacher_id = %s
        """
        cursor.execute(class_query, (teacher_id,))
        classes = cursor.fetchall()

        if not classes:
            return jsonify({"message": "No classes found for this teacher."}), 404

        quizzes_by_class = {}

        # Fetch quizzes for each class and their completion status
        for class_item in classes:
            class_id = class_item['class_id']
            class_name = class_item['class_name']

            quiz_query = """
            SELECT q.quiz_id, q.title, q.active
            FROM quizzes q
            WHERE q.class_id = %s
            """
            cursor.execute(quiz_query, (class_id,))
            quizzes = cursor.fetchall()

            quizzes_with_details = []
            for quiz in quizzes:
                quiz_id = quiz['quiz_id']
                quiz_title = quiz['title']
                quiz_active = quiz['active']

                # Get the total number of students and how many have completed the quiz
                cursor.execute("SELECT COUNT(*) AS total_students FROM student_quizzes WHERE quiz_id = %s", (quiz_id,))
                total_students = cursor.fetchone()['total_students']

                cursor.execute("SELECT COUNT(*) AS completed_students FROM student_quizzes WHERE quiz_id = %s AND completed = 1", (quiz_id,))
                completed_students = cursor.fetchone()['completed_students']

                completion_percentage = (completed_students / total_students * 100) if total_students > 0 else 0

                average_score = None
                if quiz_active == "Complete":
                    cursor.execute("SELECT AVG(score) AS average_score FROM student_quizzes WHERE quiz_id = %s AND completed = 1", (quiz_id,))
                    average_score = cursor.fetchone()['average_score'] or 0

                quizzes_with_details.append({
                    "quiz_id": quiz_id,
                    "title": quiz_title,
                    "active": quiz_active,
                    "completion_percentage": completion_percentage,
                    "average_score": average_score
                })

            quizzes_by_class[class_name] = quizzes_with_details

        cursor.close()

        if not any(quizzes_by_class.values()):
            return jsonify({"message": "No quizzes found for the given teacher's classes."}), 404

        return jsonify(quizzes_by_class), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get quiz details and student performance for a specific quiz
@teacher_routes.route('/getQuizDetails', methods=['POST'])
def getQuizDetails():
    try:
        data = request.get_json()
        token = data['token']
        quiz_id = data['quiz_id']
        teacher_id = get_id(token)

        if not teacher_id or not quiz_id:
            return jsonify({"error": "Missing teacher_id or quiz_id parameter"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to fetch student performance for the quiz
        student_quiz_query = """
        SELECT s.student_id, s.student_name, sq.score, sq.completed
        FROM students s
        JOIN student_quizzes sq ON s.student_id = sq.student_id
        WHERE sq.quiz_id = %s
        """
        cursor.execute(student_quiz_query, (quiz_id,))
        student_details = cursor.fetchall()

        # Query to fetch questions for the quiz
        quiz_questions_query = """
        SELECT question_id, question_text
        FROM quiz_questions
        WHERE quiz_id = %s
        """
        cursor.execute(quiz_questions_query, (quiz_id,))
        quiz_questions = cursor.fetchall()

        cursor.close()

        if not student_details:
            return jsonify({"message": "No students found for the specified quiz."}), 404

        return jsonify({
            "students": student_details,
            "quiz_questions": quiz_questions
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get feedback on quizzes for completed classes
@teacher_routes.route('/teacherFeedback', methods=['POST'])
def teacher_feedback():
    try:
        data = request.get_json()
        token = data['token']
        teacher_id = get_id(token)

        if not teacher_id:
            return jsonify({"error": "Invalid token or teacher_id not found."}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to fetch all class IDs and names taught by the teacher
        class_query = """
        SELECT class_id, class_name
        FROM classes
        WHERE teacher_id = %s
        """
        cursor.execute(class_query, (teacher_id,))
        classes = cursor.fetchall()

        if not classes:
            return jsonify({"message": "No classes found for this teacher."}), 404

        quizzes_by_class = {}

        # Fetch quizzes for each class with 'Complete' status and average scores
        for class_item in classes:
            class_id = class_item['class_id']
            class_name = class_item['class_name']

            quiz_query = """
            SELECT q.quiz_id, q.title, q.due_date
            FROM quizzes q
            WHERE q.class_id = %s AND q.active = 'Complete'
            """
            cursor.execute(quiz_query, (class_id,))
            quizzes = cursor.fetchall()

            quizzes_with_details = []
            for quiz in quizzes:
                quiz_id = quiz['quiz_id']
                quiz_title = quiz['title']
                due_date = quiz['due_date']

                cursor.execute("""
                    SELECT AVG(sq.score) AS average_score
                    FROM student_quizzes sq
                    WHERE sq.quiz_id = %s AND sq.completed = 1
                """, (quiz_id,))
                quiz_details = cursor.fetchone()

                average_score = quiz_details['average_score'] or 0

                quizzes_with_details.append({
                    "quiz_id": quiz_id,
                    "title": quiz_title,
                    "average_score": average_score,
                    "due_date": due_date
                })

            quizzes_by_class[class_name] = quizzes_with_details

        cursor.close()

        if not any(quizzes_by_class.values()):
            return jsonify({"message": "No quizzes found for the given teacher's classes."}), 404

        return jsonify(quizzes_by_class), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
