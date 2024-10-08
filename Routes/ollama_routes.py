from flask import Blueprint, jsonify, request
import ollama
from Routes.rag import *

ollama_routes = Blueprint('routes', __name__)


# Get Response with just Ollama
def get_response(query):
    response = ollama.chat(model='llama3', messages=[
        {
            'role': 'user',
            'content': query,
        },
    ])

    return jsonify({"message": response['message']['content']})


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

    query = f"""Provide a single sentence of feedback for the following student based on their quiz result:
    - Student Name: {student}
    - Result: {result}% 
    """
    return query


def get_feedbackPrompt(query):
    prompt = f"""You are a grade school math teacher providing feedback on a student's quiz results.

    Your goal is to generate a single sentence of feedback that is appropriate for a grade school student.

    Guidelines:
    1. If the result is 90% or higher, provide positive feedback.
    2. If the result is between 50% and 89%, provide encouraging feedback.
    3. If the result is below 50%, provide supportive feedback that encourages the student to learn more.

    Constraints:
    1. Do not give any further explanation or suggestions for improvement.
    2. Avoid mentioning that you were given specific context.
    3. Ensure the feedback is friendly and encouraging, never rude or discouraging.

    Please respond to the following request:

    {query}
    """
    return prompt
