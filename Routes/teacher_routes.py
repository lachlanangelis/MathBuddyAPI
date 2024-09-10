import MySQLdb.cursors
from decorator import *
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask import Blueprint, jsonify, current_app
import json


teacher_routes = Blueprint('teacher_routes', __name__)

def get_mysql():
    return current_app.config['mysql']


# endpoint to display the classes the teacher teaches
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

#function to create a class and store it in db

@teacher_routes.route('/create_class', methods=['POST'])
def create_class():
    try:
        data = request.get_json()
        class_name = data.get('class_name')
        class_grade = data.get('class_grade')
        token = data['token']
        teacher_id = get_id(token)

        if not class_name or not teacher_id:
            return jsonify({"error": "Missing class_name or teacher_id"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor()
        query = "INSERT INTO classes (class_name, teacher_id, class_grade) VALUES (%s, %s, %s)"
        cursor.execute(query, (class_name, teacher_id, class_grade))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Class created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#function to add students to a class and update db
@teacher_routes.route('/update_students_class', methods=['POST'])
def update_students_class():
    try:
        # Get the data from the request
        data = request.json
        student_ids = data.get('student_ids')
        new_class_id = data.get('new_class_id')

        # Validate the input
        if not student_ids or not new_class_id:
            return jsonify({"error": "Missing student_ids or new_class_id"}), 400

        # Ensure student_ids is a list
        if not isinstance(student_ids, list):
            return jsonify({"error": "student_ids must be a list"}), 400

        # Get the MySQL connection
        mysql = get_mysql()
        cursor = mysql.connection.cursor()

        # Prepare the query
        query = "UPDATE students SET class_id = %s WHERE student_id = %s"

        # Update each student's class
        for student_id in student_ids:
            cursor.execute(query, (new_class_id, student_id))

        # Commit the transaction
        mysql.connection.commit()

        # Close the cursor
        cursor.close()

        return jsonify({"message": "Added students to class successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#endpoint to display feedback for each class quiz
@teacher_routes.route('/class_feedback', methods=['GET'])
def get_class_feedback():

    try:
        class_id = request.args.get('class_id')
        quiz_id = request.args.get('quiz_id')
        
        if not class_id or not quiz_id:
            return jsonify({"error": "Missing class_id or quiz_id parameter"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
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


#endpoint to display lessons 

@teacher_routes.route('/teacher_lessons', methods=['POST'])
def get_teacher_lessons():
    try:
        data = request.get_json()
        token = data['token']
        teacher_id = get_id(token)
        #teacher_id = request.args.get('teacher_id')
        if not teacher_id:
            return jsonify({"error": "Missing teacher_id parameter"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to fetch lessons for the given teacher
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

#endpoint to display personal information of teachers
@teacher_routes.route('/teacherInfo', methods=['POST'])
def get_teacher_by_id():
    try:
        data = request.get_json()
        token = data['token']
        teacher_id = get_id(token)
        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = """
        SELECT 
            t.teacher_id,
            t.teacher_name,
            t.user_id,
            u.date_of_birth,
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

#function to Edit personal information of teachers

@teacher_routes.route('/update_teacher_profile', methods=['POST'])
def update_teacher_profile():
    try:
        # Retrieve JSON data from the request
        data = request.get_json()
        token = data['token']
        teacher_id = get_id(token)
        #teacher_id = data.get('teacher_id')

        # Optional fields that can be updated
        teacher_name = data.get('teacher_name')
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

        # Validate that teacher_id is present
        if not teacher_id:
            return jsonify({"error": "Missing teacher_id parameter"}), 400

        # Get MySQL connection
        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Initialize update queries and parameters list
        update_fields = []
        parameters = []

        # Conditionally build the update query based on provided data
        if teacher_name:
            update_fields.append("t.teacher_name = %s")
            parameters.append(teacher_name)

        if date_of_birth:
            update_fields.append("u.date_of_birth = %s")
            parameters.append(date_of_birth)

        if gender:
            update_fields.append("u.gender = %s")
            parameters.append(gender)

        if full_name:
            update_fields.append("u.full_name = %s")
            parameters.append(full_name)

        if preferred_first_name:
            update_fields.append("u.preferred_first_name = %s")
            parameters.append(preferred_first_name)

        if city:
            update_fields.append("u.city = %s")
            parameters.append(city)

        if state:
            update_fields.append("u.state = %s")
            parameters.append(state)

        if postal_code:
            update_fields.append("u.postal_code = %s")
            parameters.append(postal_code)

        if address:
            update_fields.append("u.address = %s")
            parameters.append(address)

        if mobile_phone:
            update_fields.append("u.mobile_phone = %s")
            parameters.append(mobile_phone)

        if home_phone:
            update_fields.append("u.home_phone = %s")
            parameters.append(home_phone)

        if email:
            update_fields.append("u.email = %s")
            parameters.append(email)

        if password:
            update_fields.append("u.password = %s")
            parameters.append(password)

        # Ensure there is something to update
        if not update_fields:
            return jsonify({"error": "No valid fields provided for update"}), 400

        # Build the final update query
        update_query = f"""
        UPDATE teachers t
        JOIN users u ON t.user_id = u.user_id
        SET {', '.join(update_fields)}
        WHERE t.teacher_id = %s
        """
        parameters.append(teacher_id)

        # Execute the update query
        cursor.execute(update_query, tuple(parameters))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Teacher profile updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to provide additional feedback on student quizzes

@teacher_routes.route('/add_additional_feedback', methods=['POST'])
def add_additional_feedback():
    try:
        # Retrieve JSON data from the request
        data = request.get_json()
        student_id = data.get('student_id')
        teacher_id = data.get('teacher_id')
        quiz_id = data.get('quiz_id')
        additional_feedback_teacher = data.get('additional_feedback_teacher')

        # Validate that required fields are present
        if not student_id or not teacher_id or not quiz_id or not additional_feedback_teacher:
            return jsonify({"error": "Missing required parameters"}), 400

        # Get MySQL connection
        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Update or insert the feedback in the feedback table
        cursor.execute("""
            SELECT feedback_id FROM feedback
            WHERE student_id = %s AND teacher_id = %s AND quiz_id = %s
        """, (student_id, teacher_id, quiz_id))
        feedback = cursor.fetchone()

        if feedback:
            update_feedback_query = """
            UPDATE feedback
            SET additional_feedback_teacher = %s
            WHERE feedback_id = %s
            """
            cursor.execute(update_feedback_query, (additional_feedback_teacher, feedback['feedback_id']))
        else:
            insert_feedback_query = """
            INSERT INTO feedback (student_id, teacher_id, quiz_id, additional_feedback_teacher)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_feedback_query, (student_id, teacher_id, quiz_id, additional_feedback_teacher))

        # Update the additional feedback in the student_quizzes table
        cursor.execute("""
            UPDATE student_quizzes
            SET additional_feedback_teacher = %s
            WHERE student_id = %s AND quiz_id = %s
        """, (additional_feedback_teacher, student_id, quiz_id))

        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Additional feedback updated successfully in both tables"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#Route to assign a quiz to a specific class
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

        # Update the class_id for the quiz
        query = "UPDATE quizzes SET class_id = %s WHERE quiz_id = %s"
        cursor.execute(query, (class_id, quiz_id))
        mysql.connection.commit()

        # Get all students in the class
        cursor.execute("SELECT student_id FROM students WHERE class_id = %s", (class_id,))
        students = cursor.fetchall()

        # Create a student_quizzes record for each student in the class
        for student in students:
            cursor.execute("""
                INSERT INTO student_quizzes (student_id, quiz_id)
                VALUES (%s, %s)
            """, (student['student_id'], quiz_id))
        
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Quiz assigned to class and records created for each student successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
