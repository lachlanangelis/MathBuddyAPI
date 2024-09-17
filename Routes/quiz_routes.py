import concurrent.futures

import MySQLdb.cursors

from Routes.ollama_routes import *
from decorator import *

quiz_routes = Blueprint('quiz_routes', __name__)


def get_mysql():
    return current_app.config['mysql']


@quiz_routes.route('/create_quiz', methods=['POST'])
def create_quiz():
    try:
        if request.method == 'POST':
            # Retrieve the JSON data from the request
            data = request.get_json()
            topic = data.get('topic')
            number_of_questions = data.get('number_of_questions')
            class_id = data.get('class_id')  # Assume this is sent in the request body

            if topic and number_of_questions and class_id:
                # Generate the quiz
                difficulty = "medium"  # Define the difficulty level as needed
                questions = generate_quiz_questions(topic, number_of_questions, difficulty)

                mysql = get_mysql()
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

                # Insert the quiz details into the quizzes table
                cursor.execute("""
                    INSERT INTO quizzes (title, description, class_id, due_date)
                    VALUES (%s, %s, %s, NOW() + INTERVAL 7 DAY)
                """, (f"Quiz on {topic}", f"A quiz on {topic} at {difficulty} difficulty level", class_id))

                # Get the last inserted quiz ID
                quiz_id = cursor.lastrowid
                mysql.connection.commit()

                # Insert each question into the quiz_questions table with the generated quiz_id
                for question in questions:
                    cursor.execute("""
                        INSERT INTO quiz_questions (quiz_id, question_text, correct_answer)
                        VALUES (%s, %s, %s)
                    """, (quiz_id, question['question'], question['answer']))
                mysql.connection.commit()

                cursor.close()

                # Return the generated quiz ID and questions as JSON
                return jsonify({"quiz_id": quiz_id, "questions": questions}), 200
            else:
                # Return an error if any parameter is missing
                return jsonify({"error": "Missing required parameters"}), 400
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500


def generate_quiz_questions(topic, number_of_questions, difficulty):
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


# Function to generate feedback using an LLM through Ollama
# Function to generate feedback using an LLM through Ollama and store it in the database
def generate_feedback(student_id, quiz_id, student_name, grade):
    from app import app  # Import your Flask app

    with app.app_context():  # Push an application context
        try:
            # Prepare the data for the feedback generation
            results = {
                "student": student_name,
                "result": grade,
            }
            print(f"Generating feedback for: {results}")  # Debugging statement

            # Create the query for the feedback prompt
            query = get_quizQuery(results)
            print(f"Generated quiz query: {query}")  # Debugging statement

            # Create the full feedback prompt
            prompt = get_feedbackPrompt(query)
            print(f"Generated feedback prompt: {prompt}")  # Debugging statement

            # Send the request to Ollama LLM
            response = get_response(prompt)
            print(f"Response from LLM: {response}")  # Debugging statement

            # Extract JSON data from the Response object
            feedback_content = response.get_json()
            print(f"Extracted feedback content: {feedback_content}")  # Debugging statement

            # Check if 'message' is in feedback_content, since that's where the feedback is stored
            if 'message' not in feedback_content:
                raise ValueError("No 'message' field in feedback_content")  # Error handling

            # Store feedback in the database
            mysql = get_mysql()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute("""
                INSERT INTO feedback (student_id, quiz_id, feedback_text_ai)
                VALUES (%s, %s, %s)
            """, (student_id, quiz_id, feedback_content['message']))

            mysql.connection.commit()
            cursor.close()
            print("Feedback stored successfully in the database.")  # Debugging statement

            feedback = {"feedback": feedback_content}

            print(f"Final feedback object: {feedback}")  # Debugging statement

            # Return feedback as JSON response
            return jsonify(feedback)

        except Exception as e:
            print(f"Error in generate_feedback: {e}")  # Debugging statement
            return jsonify({"error": str(e)})


@quiz_routes.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    try:
        # Retrieve the JSON data from the request
        data = request.get_json()
        token = data['token']
        student_id = get_id(token)
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

        # Fetch student name
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT student_name
            FROM students
            WHERE student_id = %s
        """, (student_id,))
        student_name = cursor.fetchone()['student_name']
        cursor.close()

        # Return the grade to the student immediately
        response = jsonify({"message": "Quiz submitted and graded successfully", "grade": grade})

        # Generate feedback asynchronously and store it in the database
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(generate_feedback, student_id, quiz_id, student_name, grade)

        return response, 200

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500


@quiz_routes.route('/assign_quiz', methods=['POST'])
def assign_quiz():
    try:
        # Retrieve the JSON data from the request
        data = request.get_json()
        class_id = data.get('class_id')
        quiz_id = data.get('quiz_id')

        if not class_id or not quiz_id:
            return jsonify({"error": "Missing required parameters"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch all student IDs from the class
        cursor.execute("""
            SELECT student_id
            FROM students
            WHERE class_id = %s
        """, (class_id,))
        students = cursor.fetchall()

        if not students:
            return jsonify({"error": "No students found in the specified class"}), 404

        # Insert each student into the student_quizzes table
        for student in students:
            student_id = student['student_id']
            cursor.execute("""
                INSERT INTO student_quizzes (student_id, quiz_id, score, completed, completed_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (student_id, quiz_id, None, 0, None))

        # Update the quiz status to 'Active'
        cursor.execute("""
            UPDATE quizzes
            SET active = 'Active'
            WHERE quiz_id = %s
        """, (quiz_id,))

        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Quiz assigned to all students successfully"}), 200

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500
