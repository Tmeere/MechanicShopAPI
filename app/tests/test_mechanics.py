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

    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "Mike Johnson",
            "salary": 55000.00
        }

        response = self.client.post('/mechanics', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Mike Johnson")
        self.assertEqual(response.json['salary'], 55000.00)

    def test_get_mechanics(self):
        response = self.client.get('/mechanics')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_update_mechanic(self):
        # Create a mechanic
        mechanic_payload = {
            "name": "Mike Johnson",
            "salary": 55000.00
        }
        create_response = self.client.post('/mechanics', json=mechanic_payload)
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

    def test_delete_mechanic(self):
        # Create a mechanic
        mechanic_payload = {
            "name": "Mike Johnson",
            "salary": 55000.00
        }
        create_response = self.client.post('/mechanics', json=mechanic_payload)
        mechanic_id = create_response.json['id']

        # Delete the mechanic
        response = self.client.delete(f'/mechanics/{mechanic_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Mechanic deleted successfully")

    def test_get_mechanic_by_id(self):
        # Create a mechanic
        mechanic_payload = {
            "name": "Mike Johnson",
            "salary": 55000.00
        }
        create_response = self.client.post('/mechanics', json=mechanic_payload)
        mechanic_id = create_response.json['id']

        # Retrieve the mechanic by ID
        response = self.client.get(f'/mechanics/{mechanic_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "Mike Johnson")
        self.assertEqual(response.json['salary'], 55000.00)