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
    response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': query}])
    return response['message']['content']

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


def get_quizQuery(results):
    student = results['student']
    result = results['result']

    query = f"""Could you please provide 1 sentence feedback for the following student:
    Student Name: {student}
    Result : {result} 
    """
    return query

def get_feedbackPrompt(query):
    prompt = f"""You are a grade school math teacher that is attempting to help tutor kids on mathematical problems.
    Your goal here is to provide feedback based on quiz results.

    Generate your response by following the steps below:
    1. You are generating feedback based on results. E.g. A score of 100% is perfect, 0% is not good.
    2. Remember that you are generating feedback for grade school students.
    3. You MUST keep feedback to 1 sentence only.

    Constraints:
    1. DONT NOT PROVIDE ANY EXPLANATION ON HOW THEY CAN GET BETTER
    2. DO NOT SAY ANYTHING THAT WOULD BE CONSIDERED RUDE TO ANY CHILDREN

    CONTENT:
    {query}
    """