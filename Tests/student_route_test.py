import unittest
from flask import json
from flask_testing import TestCase
import sys
import os

# Adjust the import path to your application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app

class StudentRoutesTestCase(TestCase):
    def create_app(self):
        app = create_app()
        return app

    def setUp(self):
        self.client = self.app.test_client()

        # Attempt to log in to obtain the JWT token
        login_response = self.client.post('/login', json={
            "email": "bruh@example.com",  # Use a valid test email
            "password": "bruh"  # Use the corresponding password
        })
        
        if login_response.status_code == 200:
            self.token = login_response.json['access_token']
        else:
            self.token = None  # Handle the case where login fails
            self.fail(f"Failed to log in: {login_response.json.get('message')}")

    def test_get_student_quiz_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/getStudentQuiz', 
                                     headers=headers,
                                     json={"token": self.token})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_student_pending_quizzes_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/getStudentPendingQuizzes', 
                                     headers=headers,
                                     json={"token": self.token})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_current_quiz_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/current_quiz', 
                                     headers=headers,
                                     json={"token": self.token, "quiz_id": 1})  # Replace 1 with a valid quiz_id
        self.assertEqual(response.status_code, 200)
        self.assertIn("questions", response.json)

    def test_get_student_info_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/student', 
                                     headers=headers,
                                     json={"token": self.token})
        self.assertEqual(response.status_code, 200)
        self.assertIn("student_id", response.json)

    def test_update_student_profile_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        update_data = {
            "token": self.token,
            "student_name": "New Name"  # Provide valid data for testing
        }
        response = self.client.post('/update_student_profile', 
                                     headers=headers,
                                     json=update_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)

    def test_get_student_quiz_results_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get('/student/1/quiz_results/1',  # Replace 1 with valid IDs
                                    headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("score", response.json)

    def test_get_student_classes_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get('/student/1/classes',  # Replace 1 with a valid student ID
                                    headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("class_name", response.json)

    def test_get_student_lessons_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get('/student/1/lessons',  # Replace 1 with a valid student ID
                                    headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_complete_quiz_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/student/1/quiz/1/complete',  # Replace 1 with valid IDs
                                     headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)

    def test_get_student_completed_quizzes_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/getStudentCompletedQuizzes', 
                                     headers=headers,
                                     json={"token": self.token})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    # Add more tests for error cases, e.g., missing fields, invalid tokens, etc.

if __name__ == '__main__':
    unittest.main()
