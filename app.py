from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import ollama
import bcrypt
import json
import logging
import requests
from rag import generate_rag_response, extract_context

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'mathbuddy.ctm8ysykaehl.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'mathbuddy123'
app.config['MYSQL_DB'] = 'mathbuddy'

mysql = MySQL(app)


@app.route('/')
def hello_world():
    # put application's code here
    return 'Hello World!'


@app.route('/getResponse')
def get_response():
    response = ollama.chat(model='llama3', messages=[
        {
            'role': 'user',
            'content': 'Who are you in 1 line?',
        },
    ])
    return jsonify(response['message']['content'])


@app.route('/query', methods=['POST'])
def respond_to_query():
    if request.method == 'POST':
        # Retrieve the JSON data from the request
        data = request.get_json()
        query = data.get('query')

        if query:
            # Extract context related to the query
            context = extract_context(query)

            # Generate a response using the context and query
            response = generate_rag_response(context, query)

            # Return the response as JSON
            return jsonify({"response": response})
        else:
            # Return an error if no query was provided
            return jsonify({"error": "No query provided"}), 400


# Generate and store a quiz question
@app.route('/gen_ques', methods=['POST'])
def genQues():
    if request.method == 'POST':
        # Retrieve the JSON data from the request
        data = request.get_json()
        query = data.get('query')
        quiz_id = data.get('quiz_id')

        if query:
            # Extract context related to the query
            context = extract_context(query)

            # Generate a response using the context and query
            response = generate_rag_response(context, query)

            question = response
            question_text = question

            question = "Give just the answer to " + question
            # generate answer
            context = extract_context(question)
            response = generate_rag_response(context, question)

            # Store the quiz question and answer in the database
            correct_answer = response

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("INSERT INTO quiz_questions (quiz_id, question_text, correct_answer) VALUES (%s, %s, %s)",
                           (quiz_id, question_text, correct_answer))
            mysql.connection.commit()

            # Return the response as JSON
            return jsonify({"question": question_text, "answer": response})
        else:
            # Return an error if no query was provided
            return jsonify({"error": "No query provided"}), 400


# Create a quiz with multiple questions
@app.route('/create_quiz', methods=['POST'])
def create_quiz():
    if request.method == 'POST':
        # Retrieve the JSON data from the request
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        topic = data.get('topic')
        number_of_questions = data.get('number_of_questions')
        difficulty = data.get('difficulty')

        if quiz_id and topic and number_of_questions and difficulty:
            # Generate the quiz
            questions = generate_quiz_questions(quiz_id, topic, number_of_questions, difficulty)

            # Return the generated quiz as JSON
            return jsonify({"quiz_id": quiz_id, "questions": questions})
        else:
            # Return an error if any parameter is missing
            return jsonify({"error": "Missing required parameters"}), 400


def generate_quiz_questions(quiz_id, topic, number_of_questions, difficulty):
    questions = []
    for i in range(number_of_questions):
        # Create a query for generating each question based on the topic and difficulty
        query = f"Generate a {difficulty} level question on {topic}"

        # Extract context related to the query
        context = extract_context(query)

        # Generate a response using the context and query
        response = generate_rag_response(context, query)
        question_text = response

        # Generate the answer for the question
        answer_query = f"Give just the answer to: {question_text}"
        context = extract_context(answer_query)
        answer_response = generate_rag_response(context, answer_query)
        correct_answer = answer_response

        # Store the quiz question and answer in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO quiz_questions (quiz_id, question_text, correct_answer) VALUES (%s, %s, %s)",
                       (quiz_id, question_text, correct_answer))
        mysql.connection.commit()

        # Add the question and answer to the questions list
        questions.append({"question": question_text, "answer": correct_answer})

    return questions


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            stored_password = user['password']
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                return jsonify({"message": "Login successful"}), 200
            else:
                return jsonify({"message": "Invalid credentials"}), 401
        else:
            return jsonify({"message": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        password = data.get('password')
        email = data.get('email')
        role = data.get('role')

        # Validate the input
        if not password or not email or not role:
            return jsonify({"error": "Missing required fields"}), 400

        # Check if the email already exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            return jsonify({"error": "Email already exists"}), 400

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert the new user into the database
        cursor.execute("INSERT INTO users (password, email, role) VALUES (%s, %s, %s)",
                       (hashed_password.decode('utf-8'), email, role))
        mysql.connection.commit()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Database Query functions and routes
def fetch_data_from_table(table_name):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    cur.close()
    return rows


@app.route('/tables', methods=['GET'])
def get_tables():
    cur = mysql.connection.cursor()
    cur.execute("SHOW TABLES")
    tables = cur.fetchall()
    table_list = [table[0] for table in tables]
    cur.close()
    return jsonify(table_list)


@app.route('/tables/<table_name>', methods=['GET'])
def get_table_data(table_name):
    try:
        data = fetch_data_from_table(table_name)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# To access the data use /tables/<tablename>
@app.route('/classes', methods=['GET'])
def get_classes():
    data = fetch_data_from_table('classes')
    return jsonify(data)


@app.route('/feedback', methods=['GET'])
def get_feedback():
    data = fetch_data_from_table('feedback')
    return jsonify(data)


@app.route('/lessons', methods=['GET'])
def get_lessons():
    data = fetch_data_from_table('lessons')
    return jsonify(data)


@app.route('/parents', methods=['GET'])
def get_parents():
    data = fetch_data_from_table('parents')
    return jsonify(data)


@app.route('/quizzes', methods=['GET'])
def get_quizzes():
    data = fetch_data_from_table('quizzes')
    return jsonify(data)


@app.route('/quiz_questions', methods=['GET'])
def get_quiz_questions():
    data = fetch_data_from_table('quiz_questions')
    return jsonify(data)


@app.route('/students', methods=['GET'])
def get_students():
    data = fetch_data_from_table('students')
    return jsonify(data)


@app.route('/student_quizzes', methods=['GET'])
def get_student_quizzes():
    data = fetch_data_from_table('student_quizzes')
    return jsonify(data)


@app.route('/teachers', methods=['GET'])
def get_teachers():
    data = fetch_data_from_table('teachers')
    return jsonify(data)


@app.route('/users', methods=['GET'])
def get_users():
    data = fetch_data_from_table('users')
    return jsonify(data)


if __name__ == '__main__':
    app.run()