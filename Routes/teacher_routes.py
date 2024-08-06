import MySQLdb.cursors
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask import Blueprint, jsonify, current_app

teacher_routes = Blueprint('teacher_routes', __name__)

def get_mysql():
    return current_app.config['mysql']


#endpoint to display the classes the teacher teaches

@teacher_routes.route('/teacher_classes', methods=['GET'])
def get_teacher_classes():
    try:
        teacher_id = request.args.get('teacher_id')
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
        teacher_id = data.get('teacher_id')

        if not class_name or not teacher_id:
            return jsonify({"error": "Missing class_name or teacher_id"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor()
        query = "INSERT INTO classes (class_name, teacher_id) VALUES (%s, %s)"
        cursor.execute(query, (class_name, teacher_id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Class created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#TODO add a function to add students to a class and update db

#TODO endpoint to display feedback for each class quiz

@teacher_routes.route('/class_feedback', methods=['GET'])
def get_class_feedback():
    try:
        class_id = request.args.get('class_id')
        if not class_id:
            return jsonify({"error": "Missing class_id parameter"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fix this part later query = 
        # cursor.execute(query, (class_id,))
        result = cursor.fetchall()
        cursor.close()

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"message": "No feedback found for the given class_id"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#TODO endpoint to display lessons 

#TODO endpoint to display personal information of teachers

#TODO add function to Edit personal information of teachers
