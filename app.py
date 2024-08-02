from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import ollama
import bcrypt
from Routes.rag import generate_rag_response, extract_context
from Routes.quiz_routes import quiz_routes

app = Flask(__name__)

app.register_blueprint(quiz_routes)

app.config['MYSQL_HOST'] = 'mathbuddy.ctm8ysykaehl.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'mathbuddy123'
app.config['MYSQL_DB'] = 'mathbuddy'

mysql = MySQL(app)

# The following are basic functionality routes
@app.route('/')
def hello_world():
    # put application's code here
    return 'Hello World!'


# Get Response with just Ollama
@app.route('/getResponse')
def get_response():
    response = ollama.chat(model='llama3', messages=[
        {
            'role': 'user',
            'content': 'Who are you in 1 line?',
        },
    ])
    return jsonify(response['message']['content'])


# Get Response through RAG App
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


if __name__ == '__main__':
    app.run()
