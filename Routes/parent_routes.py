#Authors Lachlan,Zuhayer, Raul
import MySQLdb.cursors
from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required, decode_token
from decorator import *

parent_routes = Blueprint('parent_routes', __name__)

def get_mysql():
    return current_app.config['mysql']

# Helper function to extract parent_id from token
def get_parent_id_from_token(token):
    decoded_token = decode_token(token)
    return decoded_token['sub']['user_id']

# Route to display the child information of the parent
@parent_routes.route('/child_info', methods=['POST'])
@jwt_required()
def get_child_info():
    try:
        data = request.get_json()
        token = data.get('token')
        if not token:
            return jsonify({"error": "Missing token"}), 400

        parent_id = get_id(token)

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        query = '''
        SELECT 
            s.student_id,
            s.student_name,
            c.class_name,
            u.school_name
        FROM 
            students s
        JOIN 
            classes c ON s.class_id = c.class_id
        JOIN 
            parents p ON s.student_id = p.child_id
        JOIN 
            users u ON u.user_id = s.user_id
        WHERE 
            p.parent_id = %s
        '''
        
        cursor.execute(query, (parent_id,))
        child_info = cursor.fetchone()
        cursor.close()

        if child_info:
            return jsonify(child_info), 200
        else:
            return jsonify({"message": "No information found for the given parent_id"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to display pending tasks of the child 
@parent_routes.route('/get_pending_tasks', methods=['POST'])
@jwt_required()
def get_pending_tasks():
    try:
        data = request.get_json()
        token = data.get('token')
        if not token:
            return jsonify({"error": "Missing token"}), 400

        parent_id = get_id(token)

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        sql_query = '''
        SELECT 
            q.quiz_id,
            q.title AS quiz_title,
            q.description AS quiz_description,
            q.due_date AS quiz_due_date
        FROM 
            quizzes q
        JOIN 
            classes c ON q.class_id = c.class_id
        JOIN 
            students s ON s.class_id = c.class_id
        LEFT JOIN 
            student_quizzes sq ON s.student_id = sq.student_id AND q.quiz_id = sq.quiz_id
        WHERE 
            s.student_id IN (SELECT child_id FROM parents WHERE parent_id = %s)
            AND sq.score IS NULL
        '''

        cursor.execute(sql_query, (parent_id,))
        pending_tasks = cursor.fetchall()

        cursor.close()

        if pending_tasks:
            return jsonify(pending_tasks), 200
        else:
            return jsonify({"message": "No pending quizzes found for the child"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to display Progress report
@parent_routes.route('/get_child_progress', methods=['POST'])
@jwt_required()
def get_child_quiz_scores():
    try:
        data = request.get_json()
        token = data.get('token')
        if not token:
            return jsonify({"error": "Missing token"}), 400

        parent_id = get_id(token)

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        sql_query = '''
        SELECT 
            q.quiz_id,
            q.title AS quiz_title,
            sq.score
        FROM 
            student_quizzes sq
        JOIN 
            quizzes q ON sq.quiz_id = q.quiz_id
        JOIN 
            students s ON sq.student_id = s.student_id
        WHERE 
            s.student_id IN (SELECT child_id FROM parents WHERE parent_id = %s)
        '''

        cursor.execute(sql_query, (parent_id,))
        quiz_scores = cursor.fetchall()

        cursor.close()

        if quiz_scores:
            return jsonify(quiz_scores), 200
        else:
            return jsonify({"message": "No quiz scores found for the child"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to display Child quizzes
@parent_routes.route('/get_completed_quizzes', methods=['POST'])
@jwt_required()
def get_completed_quizzes():
    try:
        data = request.get_json()
        token = data.get('token')
        if not token:
            return jsonify({"error": "Missing token"}), 400

        parent_id = get_id(token)

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        query = """
        SELECT 
            q.quiz_id AS quiz_id,
            q.title AS quiz_title,
            s.student_name AS child_name
        FROM 
            parents p
        JOIN 
            students s ON p.child_id = s.student_id
        JOIN 
            student_quizzes sq ON s.student_id = sq.student_id
        JOIN 
            quizzes q ON sq.quiz_id = q.quiz_id
        WHERE 
            p.parent_id = %s AND sq.score IS NOT NULL
        """

        cursor.execute(query, (parent_id,))
        completed_quizzes = cursor.fetchall()
        cursor.close()

        if completed_quizzes:
            return jsonify(completed_quizzes), 200
        else:
            return jsonify({"message": "No completed quizzes found for the given parent_id"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to display child feedback on a specific quiz
@parent_routes.route('/get_child_quiz_feedback', methods=['POST'])
@jwt_required()
def get_child_quiz_feedback():
    try:
        data = request.get_json()
        token = data.get('token')
        quiz_id = data.get('quiz_id')

        if not token or not quiz_id:
            return jsonify({"error": "Missing token or quiz_id parameter"}), 400

        parent_id = get_id(token)

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        query = """
        SELECT 
            sq.student_id,
            s.student_name,
            q.title AS quiz_title,
            sq.score,
            sq.feedback AS student_feedback,
            sq.additional_feedback_teacher
        FROM 
            parents p
        JOIN 
            students s ON p.child_id = s.student_id
        JOIN 
            student_quizzes sq ON s.student_id = sq.student_id
        JOIN 
            quizzes q ON sq.quiz_id = q.quiz_id
        WHERE 
            p.parent_id = %s AND sq.quiz_id = %s
        """

        cursor.execute(query, (parent_id, quiz_id))
        feedback = cursor.fetchall()
        cursor.close()

        if feedback:
            return jsonify(feedback), 200
        else:
            return jsonify({"message": "No feedback found for the given parent_id and quiz_id"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to display parent information
@parent_routes.route('/parent_info', methods=['POST'])
@jwt_required()
def get_parent_info():
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({"error": "Missing token"}), 400

        parent_id = get_id(token)
        print(parent_id)

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        query = """
        SELECT 
            p.parent_name,
            u.full_name,
            u.preferred_first_name,
            u.date_of_birth,
            u.gender,
            u.address,
            u.city,
            u.state,
            u.postal_code,
            u.mobile_phone,
            u.home_phone,
            u.email,
            u.school_name
        FROM 
            parents p
        JOIN 
            users u ON p.user_id = u.user_id
        WHERE 
            p.parent_id = %s
        """
        
        cursor.execute(query, (parent_id,))
        parent_info = cursor.fetchone()
        cursor.close()

        if parent_info:
            return jsonify(parent_info), 200
        else:
            return jsonify({"message": "No parent found with the given parent_id"}), 404
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to edit parent information
@parent_routes.route('/update_parent_info', methods=['POST'])
@jwt_required()
def update_parent_info():
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({"error": "Missing token"}), 400

        parent_id = get_id(token)

        # Optional fields that can be updated
        parent_name = data.get('parent_name')
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

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Initialize update queries and parameters list
        update_fields_parents = []
        update_fields_users = []
        parameters_parents = []
        parameters_users = []

        # Conditionally build the update query based on provided data
        if parent_name:
            update_fields_parents.append("parent_name = %s")
            parameters_parents.append(parent_name)

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

        # Ensure there is something to update
        if not update_fields_parents and not update_fields_users:
            return jsonify({"error": "No valid fields provided for update"}), 400

        # Update the parents table
        if update_fields_parents:
            update_parents_query = f"""
            UPDATE parents
            SET {', '.join(update_fields_parents)}
            WHERE parent_id = %s
            """
            parameters_parents.append(parent_id)
            cursor.execute(update_parents_query, tuple(parameters_parents))

        # Update the users table
        if update_fields_users:
            cursor.execute("""
                SELECT user_id FROM parents WHERE parent_id = %s
            """, (parent_id,))
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

        return jsonify({"message": "Parent information updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
