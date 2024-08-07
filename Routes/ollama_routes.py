from flask import Blueprint, jsonify, request
import ollama
from Routes.rag import *

ollama_routes = Blueprint('routes', __name__)


# Get Response with just Ollama
@ollama_routes.route('/getResponse')
def get_response(query):
    response = ollama.chat(model='llama3', messages=[
        {
            'role': 'user',
            'content': query,
        },
    ])
    return jsonify(response['message']['content'])

def get_answer(query):
    response = ollama.generate(model='llama3', prompt=query)
    return jsonify({"answer":response})

# Get Response through RAG App
@ollama_routes.route('/query', methods=['POST'])
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
