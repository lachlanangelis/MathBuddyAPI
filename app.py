from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
import ollama

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mathbuddy'


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


if __name__ == '__main__':
    app.run()
