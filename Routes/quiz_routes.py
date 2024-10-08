import concurrent.futures
import MySQLdb.cursors
from Routes.ollama_routes import *
from decorator import *
from Routes.Lresources import search_articlesFunc, search_videosFunc

# Create a Blueprint for quiz-related routes
quiz_routes = Blueprint('quiz_routes', __name__)

# Helper function to get MySQL connection
def get_mysql():
    return current_app.config['mysql']

# Route to create a new quiz
@quiz_routes.route('/create_quiz', methods=['POST'])
def create_quiz():
    try:
        if request.method == 'POST':
            # Retrieve the JSON data from the request
            data = request.get_json()
            topic = data.get('topic')
            number_of_questions = data.get('number_of_questions')
            class_id = data.get('class_id')  # Class ID is assumed to be sent in the request body

            # Ensure required parameters are provided
            if topic and number_of_questions and class_id:
                # Generate quiz questions based on the topic and difficulty level
                difficulty = "medium"
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

                # Insert each question into the quiz_questions table
                for question in questions:
                    cursor.execute("""
                        INSERT INTO quiz_questions (quiz_id, question_text, correct_answer)
                        VALUES (%s, %s, %s)
                    """, (quiz_id, question['question'], question['answer']))
                mysql.connection.commit()

                cursor.close()

                # Return the generated quiz ID and questions
                return jsonify({"quiz_id": quiz_id, "questions": questions}), 200
            else:
                # Return an error if required parameters are missing
                return jsonify({"error": "Missing required parameters"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Helper function to generate quiz questions
def generate_quiz_questions(topic, number_of_questions, difficulty):
    questions = []
    for i in range(number_of_questions):
        # Create a query for generating each question based on the topic and difficulty
        query = f"Generate a {difficulty} level question on {topic}. Here are the previous questions. {questions}."

        # Extract context and generate response
        context = extract_context(query)
        response = generate_rag_response(context, query)
        question_text = response

        # Generate the answer for the question
        answer_query = (f"CONSTRAINTS:"
                        f"1. DO NOT GIVE ANY PRECEDING TEXT TO THE ANSWER"
                        f"2. THE ANSWER SHOULD ONLY BE THE NUMBER"
                        f"Give just the answer to: {question_text}")
        answer_response = get_answer(answer_query)
        correct_answer = answer_response

        # Add the question and answer to the questions list
        questions.append({"question": question_text, "answer": correct_answer})

    return questions

# Function to generate feedback using an LLM through Ollama and store it in the database
def generate_feedback(student_id, quiz_id, student_name, grade):
    from app import app  # Import the Flask app

    with app.app_context():  # Push an application context
        try:
            # Prepare the data for feedback generation
            results = {
                "student": student_name,
                "result": grade,
            }

            # Create the query and feedback prompt
            query = get_quizQuery(results)
            prompt = get_feedbackPrompt(query)

            # Send the request to Ollama LLM
            response = get_response(prompt)

            # Extract JSON data from the response
            feedback_content = response.get_json()

            # Store feedback in the database if it exists
            if 'message' not in feedback_content:
                raise ValueError("No 'message' field in feedback_content")

            mysql = get_mysql()
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute("""
                INSERT INTO feedback (student_id, quiz_id, feedback_text_ai)
                VALUES (%s, %s, %s)
            """, (student_id, quiz_id, feedback_content['message']))

            mysql.connection.commit()
            cursor.close()

            return jsonify({"feedback": feedback_content})

        except Exception as e:
            return jsonify({"error": str(e)})

# Route to submit a quiz and grade it
@quiz_routes.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    try:
        # Retrieve the JSON data from the request
        data = request.get_json()
        token = data['token']
        student_id = get_id(token)
        quiz_id = data.get('quiz_id')
        student_answers = data.get('answers')

        # Ensure required parameters are provided
        if not student_id or not quiz_id or not student_answers:
            return jsonify({"error": "Missing required parameters"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Retrieve correct answers from the database
        cursor.execute("""
            SELECT qq.question_id, qq.correct_answer
            FROM quiz_questions qq
            WHERE qq.quiz_id = %s
        """, (quiz_id,))
        correct_answers = cursor.fetchall()

        # Grade the quiz
        total_questions = len(correct_answers)
        correct_count = 0
        for question in correct_answers:
            question_id = question['question_id']
            correct_answer = question['correct_answer']
            student_answer = student_answers.get(str(question_id))
            if student_answer and str(student_answer).strip().lower() == str(correct_answer).strip().lower():
                correct_count += 1

        # Calculate grade
        grade = (correct_count / total_questions) * 100

        # Update the student_quizzes table with the score
        cursor.execute("""
            UPDATE student_quizzes
            SET score = %s, completed = 1, completed_at = NOW()
            WHERE student_id = %s AND quiz_id = %s
        """, (grade, student_id, quiz_id))
        mysql.connection.commit()
        cursor.close()

        # Fetch the student's name for feedback generation
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT student_name
            FROM students
            WHERE student_id = %s
        """, (student_id,))
        student_name = cursor.fetchone()['student_name']
        cursor.close()

        # Return the grade immediately
        response = jsonify({"message": "Quiz submitted and graded successfully", "grade": grade})

        # Generate feedback asynchronously and store it in the database
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(generate_feedback, student_id, quiz_id, student_name, grade)

        return response, 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to assign a quiz to all students in a class
@quiz_routes.route('/assign_quiz', methods=['POST'])
def assign_quiz():
    try:
        # Retrieve the JSON data from the request
        data = request.get_json()
        class_name = data.get('class_name')
        quiz_id = data.get('quiz_id')

        # Ensure required parameters are provided
        if not class_name or not quiz_id:
            return jsonify({"error": "Missing required parameters"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch the class ID based on class name
        cursor.execute("""
            SELECT class_id
            FROM classes
            WHERE class_name = %s
        """, (class_name,))
        class_data = cursor.fetchone()

        if not class_data:
            return jsonify({"error": "Class not found"}), 404

        class_id = class_data['class_id']

        # Fetch all student IDs in the class
        cursor.execute("""
            SELECT student_id
            FROM students
            WHERE class_id = %s
        """, (class_id,))
        students = cursor.fetchall()

        if not students:
            return jsonify({"error": "No students found in the specified class"}), 404

        # Assign the quiz to each student in the class
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
        return jsonify({"error": str(e)}), 500

# Route to get quiz completion details for all students in a class
@quiz_routes.route('/quiz_completion_details', methods=['POST'])
def quiz_completion_details():
    try:
        # Retrieve the JSON data from the request
        data = request.get_json()
        class_name = data.get('class_name')
        quiz_id = data.get('quiz_id')

        # Ensure required parameters are provided
        if not class_name or not quiz_id:
            return jsonify({"error": "Missing required parameters"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Fetch the class ID based on class name
        cursor.execute("""
            SELECT class_id
            FROM classes
            WHERE class_name = %s
        """, (class_name,))
        class_data = cursor.fetchone()

        if not class_data:
            return jsonify({"error": "Class not found"}), 404

        class_id = class_data['class_id']

        # Fetch all students and their quiz completion details
        cursor.execute("""
            SELECT student_id, student_name
            FROM students
            WHERE class_id = %s
        """, (class_id,))
        students = cursor.fetchall()

        result = []
        for student in students:
            student_id = student['student_id']
            student_name = student['student_name']

            # Fetch quiz completion details for each student
            cursor.execute("""
                SELECT score, completed_at
                FROM student_quizzes
                WHERE student_id = %s AND quiz_id = %s
            """, (student_id, quiz_id))
            quiz_details = cursor.fetchone()

            if quiz_details:
                # Fetch feedback for the quiz
                cursor.execute("""
                    SELECT feedback
                    FROM student_quizzes
                    WHERE student_id = %s AND quiz_id = %s
                """, (student_id, quiz_id))
                feedback = cursor.fetchone()

                result.append({
                    "student_id": student_id,
                    "student_name": student_name,
                    "completed_at": quiz_details['completed_at'],
                    "score": quiz_details['score'],
                    "feedback": feedback['feedback'] if feedback else None
                })
            else:
                # If no quiz details found for the student
                result.append({
                    "student_id": student_id,
                    "student_name": student_name,
                    "completed_at": None,
                    "score": None,
                    "feedback": None
                })

        cursor.close()
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get student quiz completion details for a parent
@quiz_routes.route('/parent_quiz_complete', methods=['POST'])
def parent_quiz_complete():
    try:
        # Retrieve the JSON data from the request
        data = request.get_json()
        token = data.get('token')
        quiz_id = data.get('quiz_id')
        student_id_param = data.get('student_id')  # Parent needs to provide student_id

        # Ensure required parameters are provided
        if not token or not quiz_id or not student_id_param:
            return jsonify({"error": "Missing required parameters"}), 400

        # Get the parent ID from the token
        parent_id = get_id(token)
        if not parent_id:
            return jsonify({"error": "Invalid token"}), 400

        mysql = get_mysql()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Validate that the parent has access to the specified student
        cursor.execute("""
            SELECT child_id AS student_id
            FROM parents
            WHERE parent_id = %s AND child_id = %s
        """, (parent_id, student_id_param))

        student = cursor.fetchone()
        if not student:
            return jsonify({"error": "Parent does not have access to this student's data"}), 403

        student_id = student.get('student_id')
        if not student_id:
            return jsonify({"error": "Student ID not found in database"}), 404

        # Get the quiz details
        cursor.execute("""
            SELECT score, completed_at
            FROM student_quizzes
            WHERE student_id = %s AND quiz_id = %s
        """, (student_id, quiz_id))
        student_quiz = cursor.fetchone()
        if not student_quiz:
            return jsonify({"error": "No quiz submission found for this student"}), 404

        student_score = student_quiz['score']
        completed_at = student_quiz['completed_at']

        # Get the feedback from the database
        cursor.execute("""
            SELECT feedback_text_ai
            FROM feedback
            WHERE student_id = %s AND quiz_id = %s
        """, (student_id, quiz_id))
        feedback_data = cursor.fetchone()
        feedback = feedback_data['feedback_text_ai'] if feedback_data else None

        # Search for related videos and articles based on the quiz topic
        quiz_name = student_quiz['title']
        topic = quiz_name.split('Quiz on ')[1] if 'Quiz on ' in quiz_name else quiz_name
        video_result = search_videosFunc(topic)
        article_result = search_articlesFunc([topic])

        cursor.close()

        # Return the required details along with related videos and articles
        return jsonify({
            "quiz_name": quiz_name,
            "student_score": student_score,
            "completed_at": completed_at,
            "feedback": feedback,
            "related_video": video_result.get('video_url'),
            "related_articles": article_result.get('articles')
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
