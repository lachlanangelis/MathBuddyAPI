#Authors Zuhayer
import unittest
from flask import json
from flask_testing import TestCase
import sys
import os

# Adjust the import path to application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app

class ParentRoutesTestCase(TestCase):
    def create_app(self):
        app = create_app()
        return app

    def setUp(self):
        self.client = self.app.test_client()

        # Attempt to log in to obtain the JWT token
        login_response = self.client.post('/login', json={
            "email": "jpork@gmail.com",  # Use a valid test email
            "password": "johnpork"  # Use the corresponding password
        })
        
        if login_response.status_code == 200:
            self.token = login_response.json['access_token']
        else:
            self.token = None  # Handle the case where login fails
            self.fail(f"Failed to log in: {login_response.json.get('message')}")

    def test_get_child_info_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/child_info', 
                                     headers=headers,
                                     json={"token": self.token})
        self.assertEqual(response.status_code, 200)
        self.assertIn("student_id", response.json)

    def test_get_child_info_missing_token(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/child_info', 
                                     headers=headers,
                                     json={"token": None})  # Send None to check for missing token
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_get_pending_tasks_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/get_pending_tasks', 
                                     headers=headers,
                                     json={"token": self.token})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_child_quiz_scores_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/get_child_progress', 
                                     headers=headers,
                                     json={"token": self.token})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_completed_quizzes_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/get_completed_quizzes', 
                                     headers=headers,
                                     json={"token": self.token})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_child_quiz_feedback_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/get_child_quiz_feedback', 
                                     headers=headers,
                                     json={"token": self.token, "quiz_id": 1})  # Replace 1 with a valid quiz_id
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_parent_info_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/parent_info', 
                                     headers=headers,
                                     json={"token": self.token})
        self.assertEqual(response.status_code, 200)
        self.assertIn("parent_name", response.json)

    def test_update_parent_info_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        update_data = {
            "token": self.token,
            "parent_name": "New Name"  # Provide valid data for testing
        }
        response = self.client.post('/update_parent_info', 
                                     headers=headers,
                                     json=update_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)


if __name__ == '__main__':
    unittest.main()
