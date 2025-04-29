# import unittest
# from app import create_app
# from app.models import db, Mechanic, Customer

# class TestServiceTickets(unittest.TestCase):
#     def setUp(self):
#         self.app = create_app("TestingConfig")
#         with self.app.app_context():
#             db.drop_all()
#             db.create_all()
#             # Add a mechanic for assignment
#             mechanic = Mechanic(name="Test Mechanic", email="mechanic@example.com", salary=50000)  # Added email
#             db.session.add(mechanic)
#             db.session.commit()
#         self.client = self.app.test_client()

#     # Test creating a service ticket with missing required fields; expects a 400 error and message about missing mechanic_ids.
#     # python -m unittest tests.test_tickets.TestServiceTickets.test_create_service_ticket_missing_fields
#     def test_create_service_ticket_missing_fields(self):
#         # Create a customer
#         customer_payload = {
#             "name": "John Doe",
#             "email": "jd@email.com",
#             "phone": "1900-01-01",
#             "password": "123"
#         }
#         self.client.post('/customers/', json=customer_payload)

#         # Log in to get the token
#         login_payload = {
#             "email": "jd@email.com",
#             "password": "123"
#         }
#         login_response = self.client.post('/customers/login', json=login_payload)
#         token = login_response.json['token']

#         # Attempt to create a service ticket with missing fields
#         ticket_payload = {
#             "vin": "1HGCM82633A123456"
#         }
#         headers = {
#             "Authorization": f"Bearer {token}"
#         }
#         response = self.client.post('/service_ticket', json=ticket_payload, headers=headers)
#         self.assertEqual(response.status_code, 400)
#         self.assertIn('mechanic_ids', response.json['message'])

#     # Test retrieving a service ticket with an invalid ID; expects a 404 error and not found message.
#     # python -m unittest tests.test_tickets.TestServiceTickets.test_get_service_ticket_invalid_id
#     def test_get_service_ticket_invalid_id(self):
#         # Attempt to retrieve a service ticket with an invalid ID
#         response = self.client.get('/service_ticket/9999')
#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(response.json['message'], "Service ticket not found")

#     # Test updating the status of a service ticket with an invalid ID; expects a 404 error and not found message.
#     # python -m unittest tests.test_tickets.TestServiceTickets.test_update_ticket_status_invalid_id
#     def test_update_ticket_status_invalid_id(self):
#         # Attempt to update a service ticket with an invalid ID
#         update_payload = {
#             "status": "Completed"
#         }
#         response = self.client.put('/service_ticket/ticket-update/9999', json=update_payload)
#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(response.json['message'], "Service ticket not found")

#     # Test assigning parts to a non-existent service ticket; expects a 404 error and not found message.
#     # python -m unittest tests.test_tickets.TestServiceTickets.test_assign_parts_to_ticket_invalid_ticket
#     def test_assign_parts_to_ticket_invalid_ticket(self):
#         # Create an inventory item
#         inventory_payload = {
#             "name": "Air Filter",
#             "price": 25.00
#         }
#         self.client.post('/inventory/items', json=inventory_payload)

#         # Attempt to assign parts to a non-existent service ticket
#         assign_payload = {
#             "service_ticket_id": 9999,
#             "quantity": 2
#         }
#         response = self.client.post('/inventory/assign-item/1', json=assign_payload)
#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(response.json['message'], "Service ticket not found")

#     # Test deleting a service ticket with an invalid ID; expects a 404 error and not found message.
#     # python -m unittest tests.test_tickets.TestServiceTickets.test_delete_service_ticket_invalid_id
#     def test_delete_service_ticket_invalid_id(self):
#         # Attempt to delete a service ticket with an invalid ID
#         response = self.client.delete('/service_ticket/9999')
#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(response.json['message'], "Service ticket not found")

#     # Test creating a service ticket with all required fields; expects 201 and correct data.
#     # python -m unittest tests.test_tickets.TestServiceTickets.test_create_service_ticket_success
#     def test_create_service_ticket_success(self):
#         # Create a customer
#         customer_payload = {
#             "name": "Jane Doe",
#             "email": "jane@email.com",
#             "phone": "1900-01-02",
#             "password": "abc"
#         }
#         self.client.post('/customers/', json=customer_payload)
#         # Log in to get the token
#         login_payload = {
#             "email": "jane@email.com",
#             "password": "abc"
#         }
#         login_response = self.client.post('/customers/login', json=login_payload)
#         token = login_response.json['token']
#         # Create service ticket
#         ticket_payload = {
#             "vin": "1HGCM82633A654321",
#             "service_date": "2025-04-29",
#             "service_description": "Oil change",
#             "customer_id": 1,
#             "mechanic_ids": [1]
#         }
#         headers = {"Authorization": f"Bearer {token}"}
#         response = self.client.post('/service_ticket', json=ticket_payload, headers=headers)
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(response.json['vin'], "1HGCM82633A654321")
#         self.assertEqual(response.json['service_description'], "Oil change")

#     # Test retrieving all service tickets; expects 200 and a list.
#     # python -m unittest tests.test_tickets.TestServiceTickets.test_get_all_service_tickets
#     def test_get_all_service_tickets(self):
#         response = self.client.get('/service_ticket')
#         self.assertEqual(response.status_code, 200)
#         self.assertIsInstance(response.json, list)

#     # Test updating the status of a service ticket with a valid ID; expects 200 and updated status.
#     # python -m unittest tests.test_tickets.TestServiceTickets.test_update_ticket_status_success
#     def test_update_ticket_status_success(self):
#         # Create a customer and ticket
#         customer_payload = {
#             "name": "Sam Smith",
#             "email": "sam@email.com",
#             "phone": "1900-01-03",
#             "password": "pass"
#         }
#         self.client.post('/customers/', json=customer_payload)
#         login_payload = {
#             "email": "sam@email.com",
#             "password": "pass"
#         }
#         login_response = self.client.post('/customers/login', json=login_payload)
#         token = login_response.json['token']
#         ticket_payload = {
#             "vin": "1HGCM82633A000000",
#             "service_date": "2025-04-29",
#             "service_description": "Brake check",
#             "customer_id": 2,
#             "mechanic_ids": [1]
#         }
#         headers = {"Authorization": f"Bearer {token}"}
#         create_response = self.client.post('/service_ticket', json=ticket_payload, headers=headers)
#         ticket_id = create_response.json['id']
#         # Update status
#         update_payload = {"status": "Completed"}
#         response = self.client.put(f'/service_ticket/ticket-update/{ticket_id}', json=update_payload)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json['status'], "Completed")

#     # Test deleting a service ticket with a valid ID; expects 200 and confirmation.
#     # python -m unittest tests.test_tickets.TestServiceTickets.test_delete_service_ticket_success
#     def test_delete_service_ticket_success(self):
#         # Create a customer and ticket
#         customer_payload = {
#             "name": "Alex Doe",
#             "email": "alex@email.com",
#             "phone": "1900-01-04",
#             "password": "xyz"
#         }
#         self.client.post('/customers/', json=customer_payload)
#         login_payload = {
#             "email": "alex@email.com",
#             "password": "xyz"
#         }
#         login_response = self.client.post('/customers/login', json=login_payload)
#         token = login_response.json['token']
#         ticket_payload = {
#             "vin": "1HGCM82633A111111",
#             "service_date": "2025-04-29",
#             "service_description": "Tire rotation",
#             "customer_id": 3,
#             "mechanic_ids": [1]
#         }
#         headers = {"Authorization": f"Bearer {token}"}
#         create_response = self.client.post('/service_ticket', json=ticket_payload, headers=headers)
#         ticket_id = create_response.json['id']
#         # Delete ticket
#         response = self.client.delete(f'/service_ticket/{ticket_id}')
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('message', response.json)
