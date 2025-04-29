from app import create_app
from app.models import db
import unittest


class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()

    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "1900-01-011",
            "password": "123"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe")

    def test_get_customers(self):
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_update_customer(self):
        # Create a customer
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "123-456-7890",
            "password": "123"
        }
        self.client.post('/customers/', json=customer_payload)

        # Log in to get the token
        login_payload = {
            "email": "jd@email.com",
            "password": "123"
        }
        login_response = self.client.post('/customers/login', json=login_payload)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn('token', login_response.json, "Login response does not contain 'token'")
        token = login_response.json['token']

        # Update the customer with the token
        update_payload = {
            "name": "John Updated",
            "email": "updated@email.com"
        }
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "John Updated")
    
    
    def test_delete_customer(self):
        # Create a customer
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "123-456-7890",
            "password": "123"
        }
        self.client.post('/customers/', json=customer_payload)
    
        # Log in to get the token
        login_payload = {
            "email": "jd@email.com",
            "password": "123"
        }
        login_response = self.client.post('/customers/login', json=login_payload)
        token = login_response.json['token']
    
        # Use the token to delete the customer
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = self.client.delete('/customers/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Customer deleted successfully")

    def test_get_customer_by_id(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "1900-01-01",
            "password": "123"
        }
        create_response = self.client.post('/customers/', json=customer_payload)
        customer_id = create_response.json['id']

        response = self.client.get(f'/customers/{customer_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "John Doe")

    def test_customer_login(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "1900-01-01",
            "password": "123"
        }
        self.client.post('/customers/', json=customer_payload)

        login_payload = {
            "email": "jd@email.com",
            "password": "123"
        }
        response = self.client.post('/customers/login', json=login_payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)