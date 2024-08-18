from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required
from Routes.rag import *
from Routes.ollama_routes import *
from decorator import role_required
import MySQLdb.cursors
from flask_mysqldb import MySQL

quiz_routes = Blueprint('quiz_routes', __name__)

def get_mysql():
    return current_app.config['mysql']

@quiz_routes.route('/create_quiz', methods=['POST'])
def create_quiz():
    try:
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

                mysql = get_mysql()
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

                # Insert the quiz details into the quizzes table
                cursor.execute("""
                    INSERT INTO quizzes (quiz_id, title, description, due_date)
                    VALUES (%s, %s, %s, NOW() + INTERVAL 7 DAY)
                """, (quiz_id, f"Quiz on {topic}", f"A quiz on {topic} at {difficulty} difficulty level"))
                mysql.connection.commit()

                # Insert each question into the quiz_questions table with auto-increment for question_id
                for question in questions:
                    cursor.execute("""
                        INSERT INTO quiz_questions (quiz_id, question_text, correct_answer)
                        VALUES (%s, %s, %s)
                    """, (quiz_id, question['question'], question['answer']))
                mysql.connection.commit()

                cursor.close()

                # Return the generated quiz as JSON
                return jsonify({"quiz_id": quiz_id, "questions": questions}), 200
            else:
                # Return an error if any parameter is missing
                return jsonify({"error": "Missing required parameters"}), 400
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500


# noinspection PyUnusedLocal
def generate_quiz_questions(quiz_id, topic, number_of_questions, difficulty):
    questions = []
    for i in range(number_of_questions):
        # Create a query for generating each question based on the topic and difficulty
        query = f"Generate a {difficulty} level question on {topic}. Here are the previous questions. {questions}."

        # Extract context related to the query
        context = extract_context(query)

        # Generate a response using the context and query
        response = generate_rag_response(context, query)
        question_text = response

        # Generate the answer for the question
        answer_query = (f"CONSTRAINTS:"
                        f"1. DO NOT GIVE ANY PRECEDING TEXT TO THE ANSWER"
                        f"2. THE ANSWER SHOULD ONLY BE THE NUMBER"
                        f"Give just the answer to: {question_text}")
        answer_response = get_answer(answer_query)
        correct_answer = answer_response

        # Store the quiz question and answer in the database

        # Add the question and answer to the questions list
        questions.append({"question": question_text, "answer": correct_answer})

    return questions

# route to grade quiz
@quiz_routes.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    try:
        # Retrieve the JSON data from the request
        data = request.get_json()
        student_id = data.get('student_id')
        quiz_id = data.get('quiz_id')
        student_answers = data.get('answers')  # Expected to be a dict with question_id as keys

        if not student_id or not quiz_id or not student_answers:
            return jsonify({"error": "Missing required parameters"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Retrieve correct answers for the quiz from the database
        cursor.execute("""
            SELECT qq.question_id, qq.correct_answer
            FROM quiz_questions qq
            WHERE qq.quiz_id = %s
        """, (quiz_id,))
        correct_answers = cursor.fetchall()

        # Initialize variables for grading
        total_questions = len(correct_answers)
        correct_count = 0

        # Compare submitted answers with correct answers
        for question in correct_answers:
            question_id = question['question_id']
            correct_answer = question['correct_answer']

            # Debugging output
            print(f"Checking question ID {question_id}: correct answer is {correct_answer}")

            # Check if the student answered this question
            student_answer = student_answers.get(str(question_id))  # Ensure key is a string for dict access
            print(f"Student's answer: {student_answer}")

            if student_answer is not None:
                if str(student_answer).strip().lower() == str(correct_answer).strip().lower():
                    correct_count += 1
            # If student_answer is None, the question was unanswered and gets no marks

        # Calculate grade as percentage
        grade = (correct_count / total_questions) * 100

        # Store the grade and mark the quiz as completed
        cursor.execute("""
            UPDATE student_quizzes
            SET score = %s, completed = 1, completed_at = NOW()
            WHERE student_id = %s AND quiz_id = %s
        """, (grade, student_id, quiz_id))
        mysql.connection.commit()
        cursor.close()

        # Return the grade to the student
        return jsonify({"message": "Quiz submitted and graded successfully", "grade": grade}), 200

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500

