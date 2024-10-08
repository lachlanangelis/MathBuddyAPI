import pytest
from flask import Flask
from flask_testing import TestCase
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app  # Now it should be able to find app.py correctly


class AuthRoutesTest(TestCase):
    def create_app(self):
        # Set up your testing configuration here
        app = create_app()
        app.config['TESTING'] = True
        return app

    def test_login_success(self):
        response = self.client.post('/login', json={
            "email": "bruh@example.com",
            "password": "bruh"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)

    def test_login_invalid_credentials(self):
        response = self.client.post('/login', json={
            "email": "bruh@example.com",
            "password": "invalid_password"
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["message"], "Invalid credentials")

    def test_signup_teacher_success(self):
        response = self.client.post('/signupTeach', json={
            "email": "new_teacher@example.com",
            "password": "newpassword",
            "full_name": "New Teacher",
            "phone": "1234567890"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["message"], "User registered successfully")

    def test_signup_student_success(self):
        response = self.client.post('/signupStu', json={
            "email": "new_student@example.com",
            "password": "newpassword",
            "full_name": "New Student",
            "phone": "0987654321"
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["message"], "Student and Parent registered successfully")

# To run the tests, you can use the command `pytest` in your terminal.
