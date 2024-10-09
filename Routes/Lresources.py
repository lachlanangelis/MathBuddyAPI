from flask import Blueprint, jsonify, request
from googlesearch import search
from youtubesearchpython import VideosSearch

Lresources = Blueprint('Lresources', __name__)

# Function to determine search query difficulty based on grade
def determine_difficulty(grade):
    if grade >= 90:
        return 'Advanced'
    elif grade >= 60:
        return 'Intermediate'
    else:
        return 'Basics of'

@Lresources.route('/search_videos', methods=['POST'])
def search_videos():
    try:
        data = request.get_json()
        topic = data.get('topic')
        grade = data.get('grade')  # Get the grade from the request

        if not topic or grade is None:
            return jsonify({"error": "No topic or grade provided"}), 400

        # Determine difficulty level based on grade
        difficulty = determine_difficulty(grade)

        # Build search query from topic and difficulty level
        search_query = difficulty + ' ' + topic

        # Initialize YouTube search
        videos_search = VideosSearch(search_query, limit=1)
        results = videos_search.result()

        if results['result']:
            # Get the first video result
            video = results['result'][0]
            video_url = video['link']
            return jsonify({"video_url": video_url}), 200
        else:
            return jsonify({"message": "No videos found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@Lresources.route('/search_articles', methods=['POST'])
def search_articles():
    try:
        data = request.get_json()
        topic = data.get('topic')
        grade = data.get('grade')  # Get the grade from the request

        if not topic or grade is None:
            return jsonify({"error": "No topic or grade provided"}), 400

        # Determine difficulty level based on grade
        difficulty = determine_difficulty(grade)

        # Build search query from topic and difficulty level
        search_query = difficulty + ' ' + topic + ' learning resources'

        # Perform Google search
        search_results = search(search_query, num_results=3)  # Limit to 3 results

        if search_results:
            return jsonify({"articles": search_results}), 200
        else:
            return jsonify({"message": "No articles found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Helper function for videos with difficulty consideration
# Updated function to search for YouTube videos based on topic and grade
def search_videosFunc(topic, grade):
    try:
        if not topic or grade is None:
            return {"error": "No topic or grade provided"}

        # Determine difficulty level based on grade
        difficulty = determine_difficulty(grade)

        # Build search query from topic and difficulty level
        search_query = difficulty + ' ' + topic

        # Initialize YouTube search
        videos_search = VideosSearch(search_query, limit=1)
        results = videos_search.result()

        if results['result']:
            # Get the first video result
            video = results['result'][0]
            video_url = video['link']
            return {"video_url": video_url}
        else:
            return {"message": "No videos found"}

    except Exception as e:
        return {"error": str(e)}

# Helper function for articles with difficulty consideration
def search_articlesFunc(topic, score, grade_level):
    try:
        if not topic or score is None or grade_level is None:
            return {"error": "No topic, score, or grade level provided"}

        # Determine the type of search query based on the student's score and grade level
        if score < 60:
            # For low scores, search for basic tutorials
            search_query = f"{topic} tutorial for grade {grade_level} -buy -price -store -shopping"
        else:
            # For higher scores, search for practice questions
            search_query = f"{topic} practice questions for grade {grade_level} -buy -price -store -shopping"

        # Perform Google search
        search_results = list(search(search_query, num_results=3))

        # Optionally filter out irrelevant domains if necessary (extend this list if needed)
        educational_domains = ['.edu', '.org', '.gov']

        filtered_results = [
            result for result in search_results
            if any(domain in result for domain in educational_domains) or 'tutorial' in result or 'questions' in result
        ]

        if filtered_results:
            return {"articles": filtered_results}
        else:
            return {"message": "No educational articles found"}

    except Exception as e:
        return {"error": str(e)}