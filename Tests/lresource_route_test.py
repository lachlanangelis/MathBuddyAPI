#Authors Zuhayer
import pytest
from flask import Flask
from flask.testing import FlaskClient
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from Routes.Lresources import Lresources

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(Lresources)
    with app.test_client() as client:
        yield client

def test_search_videos_route_success(client: FlaskClient, mocker):
    mocker.patch('Routes.Lresources.VideosSearch.result', return_value={
        "result": [{"link": "http://youtube.com/video"}]
    })
    
    response = client.post('/search_videos', json={"weak_topics": ["topic1"]})
    assert response.status_code == 200
    assert response.json['video_url'] == "http://youtube.com/video"

def test_search_videos_route_no_topics(client: FlaskClient):
    response = client.post('/search_videos', json={})
    assert response.status_code == 400
    assert response.json['error'] == "No weak topics provided"

def test_search_articles_route_success(client: FlaskClient, mocker):
    mocker.patch('Routes.Lresources.search', return_value=["http://example.com/article1", "http://example.com/article2"])
    
    response = client.post('/search_articles', json={"weak_topics": ["topic1"]})
    assert response.status_code == 200
    assert len(response.json['articles']) == 2

def test_search_articles_route_no_topics(client: FlaskClient):
    response = client.post('/search_articles', json={})
    assert response.status_code == 400
    assert response.json['error'] == "No weak topics provided"
