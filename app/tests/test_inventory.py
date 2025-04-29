from app import create_app
from app.models import db
import unittest


class TestInventory(unittest.TestCase):
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
        class TestInventory(unittest.TestCase):
            def setUp(self):
                self.app = create_app("TestingConfig")
                with self.app.app_context():
                    db.drop_all()
                    db.create_all()
                self.client = self.app.test_client()

            def test_create_inventory_item(self):
                inventory_payload = {
                    "name": "Air Filter",
                    "price": 25.00
                }
                response = self.client.post('/inventory/items', json=inventory_payload)
                self.assertEqual(response.status_code, 201)
                self.assertEqual(response.json['name'], "Air Filter")

            def test_get_inventory_items(self):
                response = self.client.get('/inventory/items')
                self.assertEqual(response.status_code, 200)
                self.assertIsInstance(response.json, list)

            def test_update_inventory_item(self):
                # Create an inventory item
                inventory_payload = {
                    "name": "Air Filter",
                    "price": 25.00
                }
                create_response = self.client.post('/inventory/items', json=inventory_payload)
                item_id = create_response.json['id']

                # Update the inventory item
                update_payload = {
                    "name": "Oil Filter",
                    "price": 30.00
                }
                response = self.client.put(f'/inventory/items/{item_id}', json=update_payload)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json['name'], "Oil Filter")

            def test_delete_inventory_item(self):
                # Create an inventory item
                inventory_payload = {
                    "name": "Air Filter",
                    "price": 25.00
                }
                create_response = self.client.post('/inventory/items', json=inventory_payload)
                item_id = create_response.json['id']

                # Delete the inventory item
                response = self.client.delete(f'/inventory/items/{item_id}')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json['message'], "Inventory item deleted successfully")

            def test_assign_inventory_item_to_ticket(self):
                # Create an inventory item
                inventory_payload = {
                    "name": "Air Filter",
                    "price": 25.00
                }
                self.client.post('/inventory/items', json=inventory_payload)

                # Create a service ticket
                ticket_payload = {
                    "vin": "1HGCM82633A123456",
                    "mechanic_ids": [1]
                }
                self.client.post('/service_ticket', json=ticket_payload)

                # Assign the inventory item to the service ticket
                assign_payload = {
                    "service_ticket_id": 1,
                    "quantity": 2
                }
                response = self.client.post('/inventory/assign-item/1', json=assign_payload)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json['message'], "Parts assigned successfully")

            def test_get_inventory_item_by_id(self):
                # Create an inventory item
                inventory_payload = {
                    "name": "Air Filter",
                    "price": 25.00
                }
                create_response = self.client.post('/inventory/items', json=inventory_payload)
                item_id = create_response.json['id']

                # Retrieve the inventory item by ID
                response = self.client.get(f'/inventory/items/{item_id}')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json['name'], "Air Filter")

    def test_get_customer_by_id(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "DOB": "1900-01-01",
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
            "DOB": "1900-01-01",
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