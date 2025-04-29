from app import create_app
from app.models import db
import unittest

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()

    # Test creating a mechanic with valid data; expects success and correct fields.
    # python -m unittest tests.test_mechanic.TestMechanic.test_create_mechanic
    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "Mike Johnson",
            "salary": 55000.00
        }
        response = self.client.post('/mechanics', json=mechanic_payload, follow_redirects=True)
        self.assertIn(response.status_code, [200, 201])
        self.assertEqual(response.json['name'], "Mike Johnson")
        self.assertEqual(response.json['salary'], 55000.00)

    # Test retrieving all mechanics; expects at least one mechanic in the list.
    # python -m unittest tests.test_mechanic.TestMechanic.test_get_mechanics
    def test_get_mechanics(self):
        # Create a mechanic first to ensure list is not empty
        mechanic_payload = {
            "name": "Test Mechanic",
            "salary": 50000.00
        }
        self.client.post('/mechanics', json=mechanic_payload, follow_redirects=True)
        response = self.client.get('/mechanics', follow_redirects=True)
        self.assertIn(response.status_code, [200, 201])
        self.assertIsInstance(response.json, list)
        self.assertTrue(any(m['name'] == "Test Mechanic" for m in response.json))

    # Test retrieving mechanics when none exist; expects an empty list.
    # python -m unittest tests.test_mechanic.TestMechanic.test_get_mechanics_empty
    def test_get_mechanics_empty(self):
        # Do not create any mechanics
        response = self.client.get('/mechanics', follow_redirects=True)
        self.assertIn(response.status_code, [200, 201])
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 0)

    # Test creating a mechanic with duplicate data; expects a 400/409/422 error.
    # python -m unittest tests.test_mechanic.TestMechanic.test_create_mechanic_duplicate
    def test_create_mechanic_duplicate(self):
        mechanic_payload = {
            "name": "Duplicate Mechanic",
            "salary": 50000.00
        }
        self.client.post('/mechanics', json=mechanic_payload, follow_redirects=True)
        response = self.client.post('/mechanics', json=mechanic_payload, follow_redirects=True)
        self.assertIn(response.status_code, [400, 409, 422])

    # Test creating a mechanic with extra fields; expects extra fields to be ignored or error.
    # python -m unittest tests.test_mechanic.TestMechanic.test_create_mechanic_extra_fields
    def test_create_mechanic_extra_fields(self):
        mechanic_payload = {
            "name": "Extra Fields",
            "salary": 60000.00,
            "extra": "should be ignored"
        }
        response = self.client.post('/mechanics', json=mechanic_payload, follow_redirects=True)
        if response.status_code in [200, 201]:
            self.assertEqual(response.json['name'], "Extra Fields")
            self.assertEqual(response.json['salary'], 60000.00)
            self.assertNotIn('extra', response.json)
        else:
            self.assertEqual(response.status_code, 400)
            self.assertIn('errors', response.json)
            self.assertIn('extra', response.json['errors'])

        mechanic_payload = {
            "name": "Mike Johnson",
            "salary": 55000.00
        }
        create_response = self.client.post('/mechanics/', json=mechanic_payload)
        mechanic_id = create_response.json['id']

        # Update the mechanic
        update_payload = {
            "name": "Michael Johnson",
            "salary": 60000.00
        }
        response = self.client.put(f'/mechanics/{mechanic_id}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Michael Johnson")
        self.assertEqual(response.json['salary'], 60000.00)


    # Test retrieving a mechanic by ID after creation; expects correct mechanic data.
    # python -m unittest tests.test_mechanic.TestMechanic.test_get_mechanic_by_id
    def test_get_mechanic_by_id(self):
        # Create a mechanic
        mechanic_payload = {
            "name": "Mike Johnson",
            "salary": 55000.00
        }
        self.client.post('/mechanics', json=mechanic_payload, follow_redirects=True)
        mechanic_id = 1  # Hard code the id to 1

        # Retrieve the mechanic by ID
        response = self.client.get(f'/mechanics/{mechanic_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Mike Johnson")
        self.assertEqual(response.json['salary'], 55000.00)

    # Test creating a mechanic with missing name; expects a 400/422 error.
    # python -m unittest tests.test_mechanic.TestMechanic.test_create_mechanic_missing_name
    def test_create_mechanic_missing_name(self):
        mechanic_payload = {
            "salary": 50000.00
        }
        response = self.client.post('/mechanics', json=mechanic_payload, follow_redirects=True)
        self.assertIn(response.status_code, [400, 422])

    
    # Test creating a mechanic with invalid salary type; expects a 400/422 error.
    # python -m unittest tests.test_mechanic.TestMechanic.test_create_mechanic_invalid_salary
    def test_create_mechanic_invalid_salary(self):
        mechanic_payload = {
            "name": "Invalid Salary",
            "salary": "not_a_number"
        }
        response = self.client.post('/mechanics', json=mechanic_payload, follow_redirects=True)
        self.assertIn(response.status_code, [400, 422])

    
    # Test updating a non-existent mechanic; expects a 404 error.
    # python -m unittest tests.test_mechanic.TestMechanic.test_update_mechanic_not_found
    def test_update_mechanic_not_found(self):
        update_payload = {
            "name": "Ghost Mechanic",
            "salary": 100000.00
        }
        response = self.client.put('/mechanics/9999', json=update_payload)
        self.assertEqual(response.status_code, 404)

    # Test deleting a non-existent mechanic; expects a 404 error.
    # python -m unittest tests.test_mechanic.TestMechanic.test_delete_mechanic_not_found
    def test_delete_mechanic_not_found(self):
        response = self.client.delete('/mechanics/9999')
        self.assertEqual(response.status_code, 404)

    
    # Test retrieving a non-existent mechanic by ID; expects a 404 error.
    # python -m unittest tests.test_mechanic.TestMechanic.test_get_mechanic_by_id_not_found
    def test_get_mechanic_by_id_not_found(self):
        response = self.client.get('/mechanics/9999')
        self.assertEqual(response.status_code, 404)
        mechanic_payload = {
            "name": "Mike Johnson",
            "salary": 55000.00
        }
        create_response = self.client.post('/mechanics/', json=mechanic_payload)
        mechanic_id = create_response.json['id']

        # Update the mechanic
        update_payload = {
            "name": "Michael Johnson",
            "salary": 60000.00
        }
        response = self.client.put(f'/mechanics/{mechanic_id}', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Michael Johnson")
        self.assertEqual(response.json['salary'], 60000.00)

    # Test deleting a mechanic after creation; expects successful deletion message.
    # python -m unittest tests.test_mechanic.TestMechanic.test_delete_mechanic
    def test_delete_mechanic(self):
        # Create a mechanic
        mechanic_payload = {
            "name": "Mike Johnson",
            "salary": 55000.00
        }
        create_response = self.client.post('/mechanics/', json=mechanic_payload) 
        self.assertIn(create_response.status_code, [200, 201], msg=f"Create failed: {create_response.data}")
        self.assertIsNotNone(create_response.json, msg=f"Response not JSON: {create_response.data}")
        mechanic_id = create_response.json['id']

        # Delete the mechanic
        response = self.client.delete(f'/mechanics/{mechanic_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Mechanic deleted successfully")

    
    # Test retrieving a mechanic by ID after creation; expects correct mechanic data.
    # python -m unittest tests.test_mechanic.TestMechanic.test_get_mechanic_by_id
    def test_get_mechanic_by_id(self):
        # Create a mechanic
        mechanic_payload = {
            "name": "Mike Johnson",
            "salary": 55000.00
        }
        self.client.post('/mechanics', json=mechanic_payload, follow_redirects=True)
        mechanic_id = 1  # Hard code the id to 1

        # Retrieve the mechanic by ID
        response = self.client.get(f'/mechanics/{mechanic_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Mike Johnson")
        self.assertEqual(response.json['salary'], 55000.00)