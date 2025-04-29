from app import create_app
from app.models import db, Customer
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
        print(response.json)
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
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Invalid email or password!')

    #Gets all Customers
    # python -m unittest tests.test_customer.TestCustomer.test_get_all_customers
    def test_get_all_customers(self):
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_user')

    
    #Deletes Customer using login Customer Details
    # python -m unittest tests.test_customer.TestCustomer.test_delete_customer
    def test_delete_customer(self):
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        response = self.client.delete('/customers/', headers=headers)
        self.assertEqual(response.status_code, 200)