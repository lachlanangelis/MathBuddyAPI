from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
import MySQLdb.cursors
import ollama

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
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


@app.route('/getCustom', methods=['POST'])
def get_customResponse():
    if request.is_json:
        data = request.get_json()
        content = data.get('content', '')

        response = ollama.chat(model='llama3', messages=[
            {
                'role': 'user',
                'content': content,
            },
        ])
        return jsonify(response['message']['content'])
    else:
        return jsonify({'error': 'Request must be JSON'}), 400


@app.route('/createQuiz', methods=['POST'])
def create_quiz():
    if request.is_json:
        data = request.get_json()
        grade = data.get('grade', '')
        topic = data.get('topic', '')

        content = ("I want you to write a 10 question math quiz for students in grade " + str(grade) + " and topic " +
                   str(topic)) + (". I want the questions to be no longer then 1 sentence. I want the questions to be"
                                  "written in an engaging format and never reused, always unique and numbered 1 "
                                  "through 10. I also want the answers to"
                                  "be written seperated by a comma at the end of the response under title answers."
                                  "The quiz does not need titles. You do not need to say Here is your quiz.")

        response = ollama.chat(model='llama3', messages=[
            {
                'role': 'user',
                'content': content,
            },
        ])
        return jsonify(response['message']['content'])
    else:
        return jsonify({'error': 'Request must be JSON'}), 400


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

#Database Query functions and routes
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
    
#To access the data use /tables/<tablename>
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
