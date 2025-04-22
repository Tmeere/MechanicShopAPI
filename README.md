# Mechanic Shop Management System

This is a Mechanic Shop Management System built using Flask, SQLAlchemy, and Marshmallow. The system provides APIs to manage customers, mechanics, inventory, and service tickets, enabling efficient handling of shop operations.

## Features

### Customer Management:
- Create, update, delete, and retrieve customer details.
- Prevent duplicate email or phone numbers.
- Secure login and password update functionality.

### Mechanic Management:
- Add, update, delete, and retrieve mechanic details.
- Automatically generate email addresses for mechanics.
- Assign and remove mechanics from service tickets.

### Service Ticket Management:
- Create service tickets with customer and mechanic assignments.
- Retrieve all service tickets or filter by status, mechanic, or pagination.
- Update service ticket status and manage assigned mechanics.

### Inventory Management:
- Add, update, delete, and retrieve inventory items.
- Assign inventory items to service tickets.
- Filter inventory by price, name, or unassigned status.

## API Endpoints

### Customers
- **POST** `/customers/`: Create a new customer.
- **GET** `/customers/`: Retrieve all customers.
- **GET** `/customers/<customer_id>`: Retrieve a customer by ID.
- **PUT** `/customers/<customer_id>`: Update a customer.
- **DELETE** `/customers/<customer_id>`: Delete a customer.
- **POST** `/customers/login`: Customer login.
- **POST** `/customers/password-update`: Update customer password.

### Mechanics
- **POST** `/mechanics/`: Add a new mechanic.
- **GET** `/mechanics/`: Retrieve all mechanics.
- **GET** `/mechanics/<mechanic_id>`: Retrieve a mechanic by ID.
- **PUT** `/mechanics/<mechanic_id>`: Update a mechanic.
- **DELETE** `/mechanics/<mechanic_id>`: Delete a mechanic.
- **POST** `/mechanics/login`: Mechanic login.
- **GET** `/mechanics/most-tickets`: Retrieve mechanics sorted by the number of assigned tickets.
- **GET** `/mechanics/search`: Search mechanics by name or salary.

### Service Tickets
- **POST** `/service_ticket/`: Create a new service ticket.
- **GET** `/service_ticket/`: Retrieve all service tickets.
- **GET** `/service_ticket/<ticket_id>`: Retrieve a service ticket by ID.
- **PUT** `/service_ticket/ticket-update/<ticket_id>`: Update the status of a service ticket.
- **PUT** `/service_ticket/<ticket_id>`: Add or remove mechanics from a service ticket.

### Inventory
- **POST** `/inventory/items`: Add a new inventory item.
- **GET** `/inventory/items`: Retrieve all inventory items or filter by criteria.
- **PUT** `/inventory/items/<item_id>`: Update an inventory item.
- **DELETE** `/inventory/items/<item_id>`: Delete an inventory item.
- **POST** `/inventory/assign-item/<inventory_id>`: Assign an inventory item to a service ticket.

## Technologies Used

### Backend:
- Flask
- Flask-SQLAlchemy
- Flask-Marshmallow
- Flask-Limiter
- Flask-Caching

### Database:
- MySQL

### Validation:
- Marshmallow


## Requirements

Install the required dependencies using the `requirements.txt` file:

```bash
pip install -r [requirements.txt](http://_vscodecontentref_/4)

##Setup Instructions
Clone the repository.
Install dependencies using pip install -r requirements.txt.
Configure the database connection in app/config.py.
Run the application using python app.py.
Access the API at http://127.0.0.1:5000.
##Notes
Ensure MySQL is running and the database is created before starting the application.
Use Postman or similar tools to test the API endpoints.

