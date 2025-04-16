from flask import request, jsonify
from app.blueprints.customers import customers_bp
from app.blueprints.service_tickets.schemas import service_tickets_schema 
from app.models import Customer, db, ServiceTicket
from app.extensions import limiter, cache
from werkzeug.security import generate_password_hash
from app.utils.util import encode_token, token_required
from .schemas import customer_schema, customers_schema
from marshmallow import ValidationError
from sqlalchemy import select

@customers_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = request.json
        email = credentials['email']
        password = credentials['password']
    except KeyError:
        return jsonify({'message': 'Invalid payload, expecting email and password'}), 400

    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalar_one_or_none()
    
    if not customer:
        return jsonify({'message': 'Email invalid or User does not exist, create an account?'})

    if customer and customer.password == password:
        auth_token = encode_token(customer.id)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'message': "Invalid email or password"}), 401
    
@customers_bp.route('/password-update', methods=['POST'])
@token_required
@limiter.limit("3 per hour")
def update_password(customer_id):
    # Fetch the customer from the database
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()

    if customer is None:
        return jsonify({"message": "Invalid customer ID. Please provide a valid customer ID."}), 404

    if not request.json:
        return jsonify({"message": "Request body is missing. Please provide the required data."}), 400

    try:
        # Validate the input data
        customer_data = customer_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": e.messages}), 400

    # Check if password is provided
    if 'password' not in customer_data:
        return jsonify({"message": "Password field is required to update the password."}), 400

    try:
        customer.password = (customer_data['password'])
    except Exception as e:
        return jsonify({"message": "An error occurred while hashing the password.", "error": str(e)}), 500

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({"message": "An error occurred while saving the changes to the database.", "error": str(e)}), 500

    return jsonify({"message": "Password updated successfully"}), 200

@customers_bp.route("/", methods=['POST'])
@limiter.limit("3 per hour")
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    existing_customer = db.session.execute(
        select(Customer).where(
            (Customer.email == customer_data['email']) | 
            (Customer.phone == customer_data['phone'])
        )
    ).scalars().first()

    if existing_customer:
        return jsonify({"message": "Email or phone number already in use"}), 400

    new_customer = Customer(
        name=customer_data['name'],
        email=customer_data['email'],
        phone=customer_data['phone'],
        password=customer_data['password']
    )

    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201


@customers_bp.route("/", methods=['GET'])
@limiter.limit("10 per minute")
@cache.cached(timeout=60)
def get_customers():
    query = select(Customer)
    result = db.session.execute(query).scalars().all()
    return customers_schema.jsonify(result), 200


@customers_bp.route("/<int:customer_id>", methods=["PUT"])
@limiter.limit("3 per hour")
def update_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()

    if customer is None:
        return jsonify({"message": "Invalid customer ID"}), 404

    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    existing_customer = db.session.execute(
        select(Customer).where(
            ((Customer.email == customer_data['email']) | 
             (Customer.phone == customer_data['phone'])) |
            (Customer.id != customer_id)
        )
    ).scalars().first()

    if existing_customer:
        return jsonify({"message": "Email or phone number already in use"}), 400

    for field, value in customer_data.items():
        setattr(customer, field, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


@customers_bp.route("/", methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()

    if customer is None:
        return jsonify({"message": "Invalid customer ID"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted customer {customer_id}"})


@customers_bp.route("/<int:customer_id>", methods=['GET'])
@limiter.limit("10 per minute")
@cache.cached(timeout=60, key_prefix=lambda: f"customer_{request.view_args['customer_id']}")
def get_customer_by_id(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()

    if customer is None:
        return jsonify({"message": "Customer not found"}), 404

    return customer_schema.jsonify(customer), 200

@customers_bp.route("/my-tickets", methods=["GET"])
@token_required
def get_customer_tickets(customer_id):
    # Query only the required fields: VIN, service info, and mechanic name
    query = select(
        ServiceTicket.vin,
        ServiceTicket.service_date,
        ServiceTicket.service_description,
        ServiceTicket.status,
    ).where(ServiceTicket.customer_id == customer_id)
    
    tickets = db.session.execute(query).all()

    if not tickets:
        return jsonify({'message': 'No Tickets were found for this user'})

    # Format the response to include only the required fields
    tickets_data = [
    {
        "vin": ticket.vin,
        "service_info": ticket.service_date,
        "description": ticket.service_description,
        "status": ticket.status.value
    }
    for ticket in tickets
]

    return jsonify(tickets_data), 200