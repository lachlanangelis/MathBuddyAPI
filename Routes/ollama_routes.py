from flask import Blueprint, jsonify, request
import ollama
from Routes.rag import *

# Create a Blueprint for Ollama-related routes
ollama_routes = Blueprint('routes', __name__)

# Function to get a response from the Ollama model based on a user query
def get_response(query):
    # Generate a chat response from the Ollama model
    response = ollama.chat(model='llama3', messages=[
        {
            'role': 'user',
            'content': query,
        },
    ])
    # Return the generated message as JSON
    return jsonify({"message": response['message']['content']})


# Function to get a raw answer (content only) from the Ollama model
def get_answer(query):
    # Generate a chat response from the Ollama model
    response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': query}])
    # Return only the content of the message
    return response['message']['content']


# Route to handle POST requests and respond to user queries using RAG (Retrieval-Augmented Generation)
@ollama_routes.route('/query', methods=['POST'])
def respond_to_query():
    if request.method == 'POST':
        # Retrieve JSON data from the request
        data = request.get_json()
        query = data.get('query')

        # Check if query is provided
        if query:
            # Extract relevant context based on the query
            context = extract_context(query)

            # Generate a RAG-based response using context and query
            response = generate_rag_response(context, query)

            # Return the generated response as JSON
            return jsonify({"response": response})
        else:
            # Return an error if no query is provided in the request
            return jsonify({"error": "No query provided"}), 400


# Function to generate a quiz feedback query based on student results
def get_quizQuery(results):
    student = results['student']
    result = results['result']

    # Format a query to request feedback based on student name and result
    query = f"""Provide a single sentence of feedback for the following student based on their quiz result:
    - Student Name: {student}
    - Result: {result}% 
    """
    return query


# Function to generate a feedback prompt for Ollama based on quiz results
def get_feedbackPrompt(query):
    # Define a structured prompt for feedback generation based on student performance
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
