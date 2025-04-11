from app.blueprints.customers import members_bp
from app.blueprints.customers.schemas import customer_schema, mechanic_schema, customers_schema, mechanics_schema, service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Customer, db
from sqlalchemy import select


@members_bp.route("/customer", methods=['POST'])
def create_customer():
    try:
        # Validate and deserialize input data
        customer_data = customer_schema.load(request.json)

        # Check if the phone number already exists
        existing_phone_customer = db.session.execute(
            select(Customer).where(Customer.phone == customer_data['phone'])
        ).scalars().first()

        if existing_phone_customer:
            return jsonify({"error": "The phone number is already associated with an account"}), 400

        # Check if the email already exists
        existing_email_customer = db.session.execute(
            select(Customer).where(Customer.email == customer_data['email'])
        ).scalars().first()

        if existing_email_customer:
            return jsonify({"error": "The email address is already associated with an account"}), 400

        # Create a new customer instance
        new_customer = Customer(
            name=customer_data['name'],
            email=customer_data['email'],
            phone=customer_data['phone']
        )

        # Add and commit the new customer to the database
        db.session.add(new_customer)
        db.session.commit()

        # Return the created customer as a response
        return customer_schema.jsonify(new_customer), 201

    except ValidationError as validation_error:
        # Handle validation errors
        return jsonify({"error": "Invalid input", "details": validation_error.messages}), 400

    except Exception as general_error:
        # Handle all other errors
        db.session.rollback()  # Rollback the transaction in case of failure
        return jsonify({"error": "An error occurred", "details": str(general_error)}), 500


@members_bp.route("/customer", methods=['GET'])
def get_all_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()
    return customers_schema.jsonify(customers), 200


@members_bp.route("/customer/<int:customer_id>", methods=['GET'])
def get_customer_by_id(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer_instance = db.session.execute(query).scalars().first()

    if customer_instance:
        return customer_schema.jsonify(customer_instance), 200
    else:
        return jsonify({"error": "Customer not found"}), 404


@members_bp.route("/customer/<int:customer_id>", methods=['PUT'])
def update_customer(customer_id):
    # Query the database for the customer
    query = select(Customer).where(Customer.id == customer_id)
    customer_instance = db.session.execute(query).scalars().first()
    
    if customer_instance is None:
        # Return a 404 error if the customer is not found
        return jsonify({"error": "Customer not found"}), 404

    try:
        # Validate and deserialize input data
        updated_data = customer_schema.load(request.json)
    except ValidationError as validation_error:
        # Return validation errors
        return jsonify({"error": "Invalid input", "details": validation_error.messages}), 400

    # Update the customer's fields with the new data
    for field, value in updated_data.items():
        setattr(customer_instance, field, value)
    
    # Commit the changes to the database
    db.session.commit()

    # Return the updated customer as a response
    return customer_schema.jsonify(customer_instance), 200


@members_bp.route("/customer/<int:customer_id>", methods=['DELETE'])
def delete_customer(customer_id):
    # Query the database for the customer
    query = select(Customer).where(Customer.id == customer_id)
    customer_instance = db.session.execute(query).scalars().first()
    
    if customer_instance is None:
        # Return a 404 error if the customer is not found
        return jsonify({"error": "Customer not found"}), 404

    # Delete the customer from the database
    db.session.delete(customer_instance)
    db.session.commit()
    
    # Return a success message
    return jsonify({"message": f"Customer with ID {customer_id} has been deleted"}), 200

