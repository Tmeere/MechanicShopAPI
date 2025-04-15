# Mechanic Shop Management System

This is a Mechanic Shop Management System built using Flask, SQLAlchemy, and Marshmallow. The system provides APIs to manage customers, mechanics, and service tickets, enabling efficient handling of shop operations.

## Features

### Customer Management:
- Create, update, delete, and retrieve customer details.
- Prevent duplicate email or phone numbers.

### Mechanic Management:
- Add, update, delete, and retrieve mechanic details.
- Automatically generate email addresses for mechanics.

### Service Ticket Management:
- Create service tickets with customer and mechanic assignments.
- Retrieve all service tickets or a specific ticket by ID.

## API Endpoints

### Customers
- **POST** `/customers/`: Create a new customer.
- **GET** `/customers/`: Retrieve all customers.
- **GET** `/customers/<customer_id>`: Retrieve a customer by ID.
- **PUT** `/customers/<customer_id>`: Update a customer.
- **DELETE** `/customers/<customer_id>`: Delete a customer.

### Mechanics
- **POST** `/mechanics/`: Add a new mechanic.
- **GET** `/mechanics/`: Retrieve all mechanics.
- **GET** `/mechanics/<mechanic_id>`: Retrieve a mechanic by ID.
- **PUT** `/mechanics/<mechanic_id>`: Update a mechanic.
- **DELETE** `/mechanics/<mechanic_id>`: Delete a mechanic.

### Service Tickets
- **POST** `/service_ticket/`: Create a new service ticket.
- **GET** `/service_ticket/`: Retrieve all service tickets.
- **GET** `/service_ticket/<ticket_id>`: Retrieve a service ticket by ID.

## Technologies Used

### Backend:
- Flask
- Flask-SQLAlchemy
- Flask-Marshmallow

### Database:
- MySQL

### Validation:
- Marshmallow
