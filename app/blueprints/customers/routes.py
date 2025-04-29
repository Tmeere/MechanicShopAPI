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

# Utility function for error handling
def handle_error(message, status_code=400, errors=None):
    response = {"message": message}
    if errors:
        response["errors"] = errors
    return jsonify(response), status_code

@customers_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = request.json
        email = credentials.get('email')
        password = credentials.get('password')

        if not email or not password:
            return handle_error('Email and password are required', 400)

        query = select(Customer).where(Customer.email == email)
        customer = db.session.execute(query).scalar_one_or_none()

        if not customer:
            return handle_error('Invalid email or user does not exist', 404)

        if customer.password != password:
            return handle_error('Invalid email or password', 401)

        auth_token = encode_token(customer.id)
        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200

    except Exception as e:
        return handle_error('An error occurred', 500, str(e))

@customers_bp.route('/password-update', methods=['POST'])
@token_required
@limiter.limit("3 per hour")
def update_password(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()

    if not customer:
        return handle_error("Invalid customer ID. Please provide a valid customer ID.", 404)

    if not request.json:
        return handle_error("Request body is missing. Please provide the required data.", 400)

    try:
        customer_data = customer_schema.load(request.json, partial=True)
    except ValidationError as e:
        return handle_error("Validation error", 400, e.messages)

    if 'password' not in customer_data:
        return handle_error("Password field is required to update the password.", 400)

    try:
        customer.password = generate_password_hash(customer_data['password'])
        db.session.commit()
        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        return handle_error("An error occurred while updating the password.", 500, str(e))

@customers_bp.route("/", methods=['POST'])
@limiter.limit("300 per hour")
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return handle_error("Validation error", 400, e.messages)

    existing_customer = db.session.execute(
        select(Customer).where(
            (Customer.email == customer_data['email']) |
            (Customer.phone == customer_data['phone'])
        )
    ).scalars().first()

    if existing_customer:
        return handle_error("Email or phone number already in use.", 400)

    try:
        new_customer = Customer(
            name=customer_data['name'],
            email=customer_data['email'],
            phone=customer_data['phone'],
            password=generate_password_hash(customer_data['password'])
        )
        db.session.add(new_customer)
        db.session.commit()
        return customer_schema.jsonify(new_customer), 201
    except Exception as e:
        return handle_error("An error occurred while creating the customer.", 500, str(e))

@customers_bp.route("/", methods=['GET'])
@limiter.limit("10 per minute")
def get_customers():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page)
        return customers_schema.jsonify(customers.items), 200
    except Exception as e:
        return handle_error("An error occurred while fetching customers.", 500, str(e))

@customers_bp.route("/", methods=["PUT"])
@token_required
@limiter.limit("3 per hour")
def update_customer(authenticated_customer_id):
    query = select(Customer).where(Customer.id == authenticated_customer_id)
    customer = db.session.execute(query).scalars().first()

    if not customer:
        return handle_error("Invalid customer ID.", 404)

    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return handle_error("Validation error", 400, e.messages)

    existing_customer = db.session.execute(
        select(Customer).where(
            ((Customer.email == customer_data['email']) |
             (Customer.phone == customer_data['phone'])) &
            (Customer.id != authenticated_customer_id)
        )
    ).scalars().first()

    if existing_customer:
        return handle_error("Email or phone number already in use.", 400)

    try:
        for field, value in customer_data.items():
            setattr(customer, field, value)
        db.session.commit()
        return customer_schema.jsonify(customer), 200
    except Exception as e:
        return handle_error("An error occurred while updating the customer.", 500, str(e))

@customers_bp.route("/", methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()

    if not customer:
        return handle_error("Invalid customer ID.", 404)

    try:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": f"Successfully deleted customer {customer_id}"}), 200
    except Exception as e:
        return handle_error("An error occurred while deleting the customer.", 500, str(e))

@customers_bp.route("/<int:customer_id>", methods=['GET'])
@limiter.limit("10 per minute")
@cache.cached(timeout=60, key_prefix=lambda: f"customer_{request.view_args['customer_id']}")
def get_customer_by_id(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()

    if not customer:
        return handle_error("Customer not found.", 404)

    return customer_schema.jsonify(customer), 200

@customers_bp.route("/my-tickets", methods=["GET"])
@token_required
def get_customer_tickets(customer_id):
    query = select(
        ServiceTicket.vin,
        ServiceTicket.service_date,
        ServiceTicket.service_description,
        ServiceTicket.status,
    ).where(ServiceTicket.customer_id == customer_id)

    tickets = db.session.execute(query).all()

    if not tickets:
        return handle_error("No tickets were found for this user.", 404)

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