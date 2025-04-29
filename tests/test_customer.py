from app import create_app
from app.models import db, Customer, ServiceTicket, Mechanic
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        """
        Set up a test app context and add a default customer to the test database.
        """
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

    # Test creating a new customer with valid data.
    # python -m unittest tests.test_customer.TestCustomer.test_create_customer
    def test_create_customer(self):
        """
        Test creating a new customer with valid data.
        Expects a 201 response and correct customer name in response.
        """
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

    # Test customer creation with missing required email field.
    # python -m unittest tests.test_customer.TestCustomer.test_invalid_creation
    def test_invalid_creation(self):
        """
        Test customer creation with missing required email field.
        Expects a 400 response and error message for missing email.
        """
        customer_payload = {
            "name": "John Doe",
            "phone": "123-456-7890",
            "password": "123"
        }

        response = self.client.post('/customers/', json=customer_payload)
        print("API response:", response.json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json['errors']['email'],
            ['Missing data for required field.']
        )

    # Test successful login with default customer credentials.
    # python -m unittest tests.test_customer.TestCustomer.test_login_customer
    def test_login_customer(self):
        """
        Test successful login with default customer credentials.
        Expects a 200 response and a success status.
        Returns the auth token for use in other tests.
        """
        credentials = {
            "email": "test@email.com",
            "password": "test"
        }

        response = self.client.post('/customers/login', json=credentials)
        print("API response:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        return response.json['auth_token']
    
    
    # Test login with invalid credentials.
    # python -m unittest tests.test_customer.TestCustomer.test_invalid_login
    def test_invalid_login(self):
        """
        Test login with invalid credentials.
        Expects a 400 response and an invalid credentials message.
        """
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_pw"
        }

        response = self.client.post('/customers/login', json=credentials)
        print("API response:", response.json)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], 'Invalid email or password!')

    # Test retrieving all customers.
    # python -m unittest tests.test_customer.TestCustomer.test_get_all_customers
    def test_get_all_customers(self):
        """
        Test retrieving all customers.
        Expects a 200 response and the default customer's name in the result.
        """
        response = self.client.get('/customers/')
        print("API response:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_user')

    
    # Test deleting a customer using authentication token.
    # python -m unittest tests.test_customer.TestCustomer.test_delete_customer
    def test_delete_customer(self):
        """
        Test deleting a customer using authentication token.
        Expects a 200 response on successful deletion.
        """
        headers = {'Authorization': "Bearer " + self.test_login_customer()}
        response = self.client.delete('/customers/', headers=headers)
        print("API response:", response.json)
        self.assertEqual(response.status_code, 200)
   
    # Test deleting a customer by specifying their ID.
    # python -m unittest tests.test_customer.TestCustomer.test_delete_customer_ID
    def test_delete_customer_ID(self):
        """
        Test deleting a customer by specifying their ID.
        Expects a 200 response and a message in the response.
        """
        customer_id = 1  # Manually provided ID
        response = self.client.delete(f'/customers/{customer_id}')
        print("API response:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
    
    
    
     # User logins in and can change there existing information
     # python -m unittest tests.test_customer.TestCustomer.test_update_customer
    def test_update_customer(self):
        """
        Test updating the logged-in customer's information.
        Expects a 200 response and updated name in the response.
        """
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
    
    
    # Test updating the logged-in customer's email to one that already exists for another customer.
    # python -m unittest tests.test_customer.TestCustomer.test_fail_update_customer
    def test_fail_update_customer(self):
        """
        Test updating the logged-in customer's email to one that already exists for another customer.
        Expects a 400 response and an error message about email already in use.
        """
        # Add a second customer with a different email
        with self.app.app_context():
            # Test creating a customer with an email that already exists (should fail)
            def test_create_customer_duplicate_email(self):
                """
                Test creating a customer with an email that already exists.
                Expects a 400 response and an error message about email already in use.
                """
                customer_payload = {
                    "name": "Jane Doe",
                    "email": "test@email.com",  # Already exists from setUp
                    "phone": "555-555-5555",
                    "password": "abc"
                }
                response = self.client.post('/customers/', json=customer_payload)
                print("API response:", response.json)
                self.assertEqual(response.status_code, 400)
                self.assertIn("already in use", response.json.get("message", ""))

            # Test creating a customer with a phone that already exists (should fail)
            #  python -m unittest tests.test_customer.TestCustomer.test_create_customer_duplicate_phone
    def test_create_customer_duplicate_phone(self):
                """
                Test creating a customer with a phone number that already exists.
                Expects a 400 response and an error message about phone already in use.
                """
                customer_payload = {
                    "name": "Jane Doe",
                    "email": "jane@email.com",
                    "phone": "101-456-7890",  # Already exists from setUp
                    "password": "abc"
                }
                response = self.client.post('/customers/', json=customer_payload)
                print("API response:", response.json)
                self.assertEqual(response.status_code, 400)
                self.assertIn("already in use", response.json.get("message", ""))

            # Test updating customer with missing required fields (should fail)
            # python -m unittest tests.test_customer.TestCustomer.test_update_customer_missing_fields
    def test_update_customer_missing_fields(self):
                """
                Test updating customer with missing required fields.
                Expects a 400 response and error messages for missing fields.
                """
                headers = {'Authorization': "Bearer " + self.test_login_customer()}
                update_payload = {
                    "name": "updated_user"
                    # Missing email, phone, password
                }
                response = self.client.put('/customers/', json=update_payload, headers=headers)
                print("API response:", response.json)
                self.assertEqual(response.status_code, 400)
                self.assertIn("errors", response.json)

            # Test deleting a customer with an invalid authentication token (should fail)
            # python -m unittest tests.test_customer.TestCustomer.test_delete_customer_invalid_token
    def test_delete_customer_invalid_token(self):
                """
                Test deleting a customer with an invalid authentication token.
                Expects a 401 or 403 response.
                """
                headers = {'Authorization': "Bearer invalidtoken"}
                response = self.client.delete('/customers/', headers=headers)
                print("API response:", response.json)
                self.assertIn(response.status_code, [401, 403])

            # Test retrieving a customer by an invalid ID (should fail)
            #  python -m unittest tests.test_customer.TestCustomer.test_get_customer_invalid_id
    def test_get_customer_invalid_id(self):
                """
                Test retrieving a customer by an invalid ID.
                Expects a 404 response.
                """
                response = self.client.get('/customers/9999')  # Assuming this ID does not exist
                print("API response:", response.json)
                self.assertEqual(response.status_code, 404)

            # Test deleting a customer by an invalid ID (should fail)
            # python -m unittest tests.test_customer.TestCustomer.test_delete_customer_invalid_id
    def test_delete_customer_invalid_id(self):
                """
                Test deleting a customer by an invalid ID.
                Expects a 404 response.
                """
                response = self.client.delete('/customers/9999')  # Assuming this ID does not exist
                print("API response:", response.json)
                self.assertEqual(response.status_code, 404)