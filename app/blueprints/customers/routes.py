from flask import request, jsonify
from app.blueprints.customers import members_bp
from app.blueprints.customers.schemas import customer_schema, customers_schema
from marshmallow import ValidationError
from app.models import Customer, db
from sqlalchemy import select


@members_bp.route("/", methods=['POST'])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Check if email or phone number is already in use
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
        phone=customer_data['phone']
    )

    db.session.add(new_customer)
    db.session.commit()

    return customer_schema.jsonify(new_customer), 201


@members_bp.route("/", methods=['GET'])
def get_customers():
    query = select(Customer)
    result = db.session.execute(query).scalars().all()
    return customers_schema.jsonify(result), 200




@members_bp.route("/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()

    if customer is None:
        return jsonify({"message": "invalid customer id"}), 404

    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Check if email or phone number is already in use by another customer
    existing_customer = db.session.execute(
        select(Customer).where(
            ((Customer.email == customer_data['email']) | 
             (Customer.phone == customer_data['phone'])) &
            (Customer.id != customer_id)
        )
    ).scalars().first()

    if existing_customer:
        return jsonify({"message": "Email or phone number already in use"}), 400

    for field, value in customer_data.items():
        setattr(customer, field, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


@members_bp.route("/<int:customer_id>", methods=['DELETE'])
def delete_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()

    if customer is None:
        return jsonify({"message": "invalid customer id"}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"successfully deleted customer {customer_id}"}), 200


@members_bp.route("/<int:customer_id>", methods=['GET'])
def get_customer_by_id(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()

    if customer is None:
        return jsonify({"message": "Customer not found"}), 404

    return customer_schema.jsonify(customer), 200