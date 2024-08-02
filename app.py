from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
from Routes.rag import generate_rag_response, extract_context
from Routes.quiz_routes import quiz_routes
from Routes.sql_routes import sql_routes
from Routes.auth_routes import auth_routes
from Routes.ollama_routes import ollama_routes

app = Flask(__name__)

app.register_blueprint(quiz_routes)
app.register_blueprint(sql_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(ollama_routes)

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


if __name__ == '__main__':
    app.run()
