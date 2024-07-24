from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import ollama
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


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()

    if user:
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


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
