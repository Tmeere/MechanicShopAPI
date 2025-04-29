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
    
    # Test creating an Inventory Item providing a name and a price.
    # python -m unittest tests.test_inventory.TestInventory.test_create_inventory_item
    def test_create_inventory_item(self):
        inventory_payload = {
            "name": "Air Filter",
            "price": 25.00
        }
        response = self.client.post('/inventory/items', json=inventory_payload)
        print("API response:", response.json)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "Air Filter")

        
    # Test getting inventory items, expects to retrieve the items inputted prior.
    # python -m unittest tests.test_inventory.TestInventory.test_get_inventory_items
    def test_get_inventory_items(self):
        self.test_create_inventory_item()
        response = self.client.get('/inventory/items')
        print("API response:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json['items'], list)

        
    # Test updating an inventory item, expects the item to be updated with new data.
    # python -m unittest tests.test_inventory.TestInventory.test_update_inventory_item
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
        print("API response:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['item']['name'], "Oil Filter")


    # Test deleting an inventory item by ID, expects successful deletion message.
    # python -m unittest tests.test_inventory.TestInventory.test_delete_inventory_item
    def test_delete_inventory_item(self):
        # Optionally, ensure the item exists first
        inventory_payload = {
            "name": "Air Filter",
            "price": 25.00
        }
        self.client.post('/inventory/items', json=inventory_payload)
        
        # Now manually use id=1
        response = self.client.delete('/inventory/items/1')
        print("API response:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "Item deleted successfully")
    
    
    # Test assigning an inventory item to a service ticket, expects success message.
    # python -m unittest tests.test_inventory.TestInventory.test_assign_inventory_item_to_ticket
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

    
    
    # Test retrieving an inventory item by ID, expects correct item data.
    # python -m unittest tests.test_inventory.TestInventory.test_get_inventory_item_by_id
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

    # Test getting a non-existent inventory item by ID, expects a 404 error.
    # python -m unittest tests.test_inventory.TestInventory.test_get_inventory_item_by_id_not_found
    def test_get_inventory_item_by_id_not_found(self):
        response = self.client.get('/inventory/items/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)

    # Test deleting a non-existent inventory item, expects a 404 error.
    # python -m unittest tests.test_inventory.TestInventory.test_delete_inventory_item_not_found
    def test_delete_inventory_item_not_found(self):
        response = self.client.delete('/inventory/items/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)


    # Test updating a non-existent inventory item, expects a 404 error.
    # python -m unittest tests.test_inventory.TestInventory.test_update_inventory_item_not_found
    def test_update_inventory_item_not_found(self):
        update_payload = {
            "name": "Nonexistent",
            "price": 99.99
        }
        response = self.client.put('/inventory/items/999', json=update_payload)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)

    
    # Test creating an inventory item with missing fields, expects an error.
    # python -m unittest tests.test_inventory.TestInventory.test_create_inventory_item_missing_fields
    def test_create_inventory_item_missing_fields(self):
        inventory_payload = {
            "name": "Incomplete"
            # Missing price
        }
        response = self.client.post('/inventory/items', json=inventory_payload)
        self.assertNotEqual(response.status_code, 201)
        self.assertIn('error', response.json)

    
    # Test assigning an inventory item to a ticket with missing service_ticket_id, expects a 400 error.
    # python -m unittest tests.test_inventory.TestInventory.test_assign_inventory_item_missing_service_ticket_id
    def test_assign_inventory_item_missing_service_ticket_id(self):
        # Create an inventory item
        inventory_payload = {
            "name": "Air Filter",
            "price": 25.00
        }
        self.client.post('/inventory/items', json=inventory_payload)
        assign_payload = {
            "quantity": 1
        }
        response = self.client.post('/inventory/assign-item/1', json=assign_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)