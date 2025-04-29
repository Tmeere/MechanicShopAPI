import unittest
from app import create_app
from app.models import db

class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()

    def test_create_service_ticket_missing_fields(self):
        # Create a customer
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "1900-01-01",
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

        # Attempt to create a service ticket with missing fields
        ticket_payload = {
            "vin": "1HGCM82633A123456"
        }
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = self.client.post('/service_ticket', json=ticket_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('mechanic_ids', response.json['message'])

    def test_get_service_ticket_invalid_id(self):
        # Attempt to retrieve a service ticket with an invalid ID
        response = self.client.get('/service_ticket/9999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Service ticket not found")

    def test_update_ticket_status_invalid_id(self):
        # Attempt to update a service ticket with an invalid ID
        update_payload = {
            "status": "Completed"
        }
        response = self.client.put('/service_ticket/ticket-update/9999', json=update_payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Service ticket not found")

    def test_assign_parts_to_ticket_invalid_ticket(self):
        # Create an inventory item
        inventory_payload = {
            "name": "Air Filter",
            "price": 25.00
        }
        self.client.post('/inventory/items', json=inventory_payload)

        # Attempt to assign parts to a non-existent service ticket
        assign_payload = {
            "service_ticket_id": 9999,
            "quantity": 2
        }
        response = self.client.post('/inventory/assign-item/1', json=assign_payload)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Service ticket not found")

    def test_delete_service_ticket_invalid_id(self):
        # Attempt to delete a service ticket with an invalid ID
        response = self.client.delete('/service_ticket/9999')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['message'], "Service ticket not found")
