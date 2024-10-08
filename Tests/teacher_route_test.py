import unittest
from flask import json
from flask_testing import TestCase
import sys
import os

# Adjust the import path to your application
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app

class TeacherRoutesTestCase(TestCase):
    def create_app(self):
        app = create_app()
        return app

    def setUp(self):
        self.client = self.app.test_client()

        # Attempt to log in to obtain the JWT token
        login_response = self.client.post('/login', json={
            "email": "bruhteach@example.com",  # Use a valid test email for a teacher
            "password": "bruh"  # Use the corresponding password
        })
        
        if login_response.status_code == 200:
            self.token = login_response.json['access_token']
        else:
            self.token = None  # Handle the case where login fails
            self.fail(f"Failed to log in: {login_response.json.get('message')}")

    def test_add_student_to_class_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/addStudent', 
                                     headers=headers,
                                     json={"student_email": "rahuld@gmail.com", "10": 1})  # Use a valid student email and class ID
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)

    def test_add_student_to_class_missing_fields(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/addStudent', 
                                     headers=headers,
                                     json={"student_email": "rahuld@gmail.com"})  # Missing new_class_id
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_get_teach_quiz_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/getTeachQuiz', 
                                     headers=headers,
                                     json={"token": self.token})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, dict)  # Assuming the response is a dictionary

    def test_get_teach_quiz_no_classes(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/getTeachQuiz', 
                                     headers=headers,
                                     json={"token": self.token})
        self.assertEqual(response.status_code, 404)
        self.assertIn("message", response.json)

    def test_get_quiz_details_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/getQuizDetails', 
                                     headers=headers,
                                     json={"token": self.token, "quiz_id": 1})  # Use a valid quiz ID
        self.assertEqual(response.status_code, 200)
        self.assertIn("students", response.json)
        self.assertIn("quiz_questions", response.json)

    def test_get_quiz_details_missing_fields(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/getQuizDetails', 
                                     headers=headers,
                                     json={"token": self.token})  # Missing quiz_id
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    def test_teacher_feedback_success(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/teacherFeedback', 
                                     headers=headers,
                                     json={"token": self.token})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, dict)  # Assuming the response is a dictionary

    def test_teacher_feedback_no_classes(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post('/teacherFeedback', 
                                     headers=headers,
                                     json={"token": self.token})
        self.assertEqual(response.status_code, 404)
        self.assertIn("message", response.json)


if __name__ == '__main__':
    unittest.main()
