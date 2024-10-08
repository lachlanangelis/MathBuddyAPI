from flask import Blueprint, jsonify, request
from googlesearch import search
from youtubesearchpython import VideosSearch

# Create a Blueprint for learning resources routes
Lresources = Blueprint('Lresources', __name__)

# Route to search YouTube videos based on weak topics
@Lresources.route('/search_videos', methods=['POST'])
def search_videos():
    try:
        # Get JSON data from the request
        data = request.get_json()
        weak_topics = data.get('weak_topics')

        # Validate if weak topics are provided
        if not weak_topics:
            return jsonify({"error": "No weak topics provided"}), 400

        # Build search query by joining weak topics
        search_query = 'Basics of '.join(weak_topics)

        # Perform YouTube search for the given query
        videos_search = VideosSearch(search_query, limit=1)
        results = videos_search.result()

        # Check if there are results and return the first video URL
        if results['result']:
            video = results['result'][0]
            video_url = video['link']
            return jsonify({"video_url": video_url}), 200
        else:
            return jsonify({"message": "No videos found"}), 404

    except Exception as e:
        # Return error response in case of an exception
        return jsonify({"error": str(e)}), 500

# Route to search articles based on weak topics
@Lresources.route('/search_articles', methods=['POST'])
def search_articles():
    try:
        # Get JSON data from the request
        data = request.get_json()
        weak_topics = data.get('weak_topics')

        # Validate if weak topics are provided
        if not weak_topics:
            return jsonify({"error": "No weak topics provided"}), 400

        # Build search query from weak topics and add "learning resources"
        search_query = ' '.join(weak_topics) + ' learning resources'

        # Perform Google search and get the top 3 results
        search_results = search(search_query, num_results=3)

        # Return the search results
        if search_results:
            return jsonify({"articles": search_results}), 200
        else:
            return jsonify({"message": "No articles found"}), 404

    except Exception as e:
        # Return error response in case of an exception
        return jsonify({"error": str(e)}), 500

# Helper function to search videos without requiring a Flask request context
def search_videosFunc(weak_topics):
    try:
        # Validate if weak topics are provided
        if not weak_topics:
            return {"error": "No weak topics provided"}

        # Build search query by adding "Basics of" to the weak topics
        search_query = 'Basics of ' + weak_topics

        # Perform YouTube search
        videos_search = VideosSearch(search_query, limit=1)
        results = videos_search.result()

        # Check if there are results and return the first video URL
        if results['result']:
            video = results['result'][0]
            video_url = video['link']
            return {"video_url": video_url}
        else:
            return {"message": "No videos found"}

    except Exception as e:
        # Return error message in case of an exception
        return {"error": str(e)}

# Helper function to search articles without requiring a Flask request context
def search_articlesFunc(weak_topics):
    try:
        # Validate if weak topics are provided
        if not weak_topics:
            return {"error": "No weak topics provided"}

        # Build search query from weak topics and add "learning resources"
        search_query = ' '.join(weak_topics) + ' learning resources'

        # Perform Google search and get the top 3 results
        search_results = list(search(search_query, num_results=3))  # Convert generator to list

        # Return the search results or a message if no results found
        if search_results:
            return {"articles": search_results}
        else:
            return {"message": "No articles found"}

    except Exception as e:
        # Return error message in case of an exception
        return {"error": str(e)}
