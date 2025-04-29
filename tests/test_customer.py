from app import create_app
from app.models import db, Customer, ServiceTicket, Mechanic
import unittest


class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.customer = Customer(
            name="test_user",
            email="test@email.com",
            phone="101-456-7890",
            password="test"
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
        self.client = self.app.test_client()

    # OKS When given Name, Email, Phone and Password, EMAIL AND PHONE MUST BE UNIQUE
    # python -m unittest tests.test_customer.TestCustomer.test_create_customer
    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "123-456-7890",
            "password": "123"
        }

        response = self.client.post('/customers/', json=customer_payload)
        print("API response:", response.json)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe")

    # Fails as the user fails to provide and Email which is required
    # python -m unittest tests.test_customer.TestCustomer.test_invalid_creation
    def test_invalid_creation(self):
        customer_payload = {
            "name": "John Doe",
            "phone": "123-456-7890",
            "password": "123"
        }

        response = self.client.post('/customers/', json=customer_payload)
        print("API response:", response.json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['email'], ['Missing data for required field.'])

    #Logins Successfully when provided with the default user credentials
    # python -m unittest tests.test_customer.TestCustomer.test_login_customer
    def test_login_customer(self):
        credentials = {
            "email": "test@email.com",
            "password": "test"
        }

        response = self.client.post('/customers/login', json=credentials)
        print("API response:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        return response.json['auth_token']
    
    
    #Logins Fails as user doesnt exist or provided incorrect details
    # python -m unittest tests.test_customer.TestCustomer.test_invalid_login
    def test_invalid_login(self):
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_pw"
        }

        response = self.client.post('/customers/login', json=credentials)
        print("API response:", response.json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Invalid email or password!')

    #Gets all Customers
    # python -m unittest tests.test_customer.TestCustomer.test_get_all_customers
    def test_get_all_customers(self):
        response = self.client.get('/customers/')
        print("API response:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_user')

    
    #Deletes Customer using login Customer Details
    # python -m unittest tests.test_customer.TestCustomer.test_delete_customer
    def test_delete_customer(self):
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        response = self.client.delete('/customers/', headers=headers)
        print("API response:", response.json)
        self.assertEqual(response.status_code, 200)
   
    #Deletes Customer using ID
    # python -m unittest tests.test_customer.TestCustomer.test_delete_customer_ID    
    def test_delete_customer_ID(self):
        customer_id = 1  # Manually provided ID
        response = self.client.delete(f'/customers/{customer_id}')
        print("API response:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
    
    
    
     # User logins in and can change there existing information
     # python -m unittest tests.test_customer.TestCustomer.test_update_customer
    def test_update_customer(self):
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        update_payload = {
            "name": "updated_user",
            "email": "test@email.com",
            "phone": "101-456-7890",
            "password": "test"
        }
        response = self.client.put('/customers/', json=update_payload, headers=headers)
        print("API response:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "updated_user")
        
    # python -m unittest tests.test_customer.TestCustomer.test_fail_update_customer   
    def test_fail_update_customer(self):
        # Add a second customer with a different email
        with self.app.app_context():
            other_customer = Customer(
                name="other_user",
                email="other@email.com",
                phone="202-555-1234",
                password="otherpass"
            )
            db.session.add(other_customer)
            db.session.commit()

        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        # Try to update the logged-in user to use the other customer's email
        update_payload = {
            "name": "updated_user",
            "email": "other@email.com",  # This email already exists for another user
            "phone": "101-456-7890",
            "password": "test"
        }
        response = self.client.put('/customers/', json=update_payload, headers=headers)
        print("API response:", response.json)
        self.assertEqual(response.status_code, 400)
        self.assertIn("already in use", response.json["message"])

