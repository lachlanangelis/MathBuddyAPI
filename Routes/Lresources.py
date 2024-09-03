import MySQLdb.cursors
from decorator import *
import ollama
from googlesearch import search
import requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from youtubesearchpython import VideosSearch

Lresources = Blueprint('Lresources', __name__)
@Lresources.route('/search_videos', methods=['POST'])
def search_videos():
    try:
        data = request.get_json()
        weak_topics = data.get('weak_topics')

        if not weak_topics:
            return jsonify({"error": "No weak topics provided"}), 400

        # Build search query from weak topics
        search_query = 'Basics of '.join(weak_topics)

        # Initialize YouTube search
        videos_search = VideosSearch(search_query, limit = 1)
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
        weak_topics = data.get('weak_topics')

        if not weak_topics:
            return jsonify({"error": "No weak topics provided"}), 400

        # Build search query from weak topics
        search_query = ' '.join(weak_topics) + ' learning resources'

        # Perform Google search
        search_results = search(search_query, num_results=3)  # Limit to 3 results

        if search_results:
            return jsonify({"articles": search_results}), 200
        else:
            return jsonify({"message": "No articles found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500