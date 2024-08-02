from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from Routes.rag import *
from decorator import role_required

quiz_routes = Blueprint('quiz_routes', __name__)


@quiz_routes.route('/create_quiz', methods=['POST'])
@jwt_required()
@role_required('teacher')
def create_quiz():
    if request.method == 'POST':
        # Retrieve the JSON data from the request
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        topic = data.get('topic')
        number_of_questions = data.get('number_of_questions')
        difficulty = data.get('difficulty')

        if quiz_id and topic and number_of_questions and difficulty:
            # Generate the quiz
            questions = generate_quiz_questions(quiz_id, topic, number_of_questions, difficulty)

            # Return the generated quiz as JSON
            return jsonify({"quiz_id": quiz_id, "questions": questions})
        else:
            # Return an error if any parameter is missing
            return jsonify({"error": "Missing required parameters"}), 400


# noinspection PyUnusedLocal
def generate_quiz_questions(quiz_id, topic, number_of_questions, difficulty):
    questions = []
    for i in range(number_of_questions):
        # Create a query for generating each question based on the topic and difficulty
        query = f"Generate a {difficulty} level question on {topic}"

        # Extract context related to the query
        context = extract_context(query)

        # Generate a response using the context and query
        response = generate_rag_response(context, query)
        question_text = response

        # Generate the answer for the question
        answer_query = f"Give just the answer to: {question_text}"
        context = extract_context(answer_query)
        answer_response = generate_rag_response(context, answer_query)
        correct_answer = answer_response

        # Store the quiz question and answer in the database

        # Add the question and answer to the questions list
        questions.append({"question": question_text, "answer": correct_answer})

    return questions
