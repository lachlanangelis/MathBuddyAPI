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
def search_articlesFunc(topic, grade):
    try:
        if not topic or grade is None:
            return {"error": "No topic or grade provided"}

        # Determine difficulty level based on grade
        difficulty = determine_difficulty(grade)

        # Build search query from topic and difficulty level
        search_query = difficulty + ' ' + topic + ' learning resources'

        # Perform Google search and convert to a list
        search_results = list(search(search_query, num_results=3))  # Convert generator to list

        if search_results:
            return {"articles": search_results}
        else:
            return {"message": "No articles found"}

    except Exception as e:
        return {"error": str(e)}
