import requests
import json
from flask import Flask, jsonify, request
import ollama

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run()
