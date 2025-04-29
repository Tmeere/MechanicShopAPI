from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Mechanic, db, ServiceTicket
from sqlalchemy import select
from app.utils.util import encode_token, token_required
from app.extensions import limiter, cache


# Utility function for error handling
def handle_error(message, status_code=400, errors=None):
    response = {"message": message}
    if errors:
        response["errors"] = errors
    return jsonify(response), status_code


@mechanics_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = request.json
        email = credentials.get('email')
        name = credentials.get('name')

        if not email or not name:
            return handle_error('Email and name are required', 400)

        query = select(Mechanic).where(Mechanic.email == email)
        mechanic = db.session.execute(query).scalar_one_or_none()

        if not mechanic:
            return handle_error('Email invalid or user does not exist, create an account?', 404)

        if mechanic.name != name:
            return handle_error('Invalid email or name', 401)

        auth_token = encode_token(mechanic.id)
        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    except Exception as e:
        return handle_error('An error occurred during login', 500, str(e))


@mechanics_bp.route("/remove-ticket/<int:ticket_id>", methods=["DELETE"])
@token_required
def remove_ticket(mechanic_id, ticket_id):
    if not mechanic_id:
        return handle_error("Unauthorized. Please log in.", 401)

    query = select(ServiceTicket).where(
        ServiceTicket.id == ticket_id,
        ServiceTicket.mechanics.any(id=mechanic_id)
    )
    ticket = db.session.execute(query).scalars().first()

    if not ticket:
        return handle_error("Ticket not found or you are not authorized to delete this ticket", 404)

    try:
        db.session.delete(ticket)
        db.session.commit()
        return jsonify({"message": f"Ticket with ID {ticket_id} successfully deleted"}), 200
    except Exception as e:
        return handle_error("An error occurred while deleting the ticket", 500, str(e))


@mechanics_bp.route("/<int:mechanic_id>", methods=['GET'])
@limiter.limit("10 per minute")
@cache.cached(timeout=60, key_prefix=lambda: f"mechanic_{request.view_args['mechanic_id']}")
def get_mechanic(mechanic_id):
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic_instance = db.session.execute(query).scalars().first()

    if not mechanic_instance:
        return handle_error("Mechanic not found", 404)

    return mechanic_schema.jsonify(mechanic_instance), 200


@mechanics_bp.route("/", methods=['GET'])
@limiter.limit("10 per minute")
def get_all_mechanics():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        query = select(Mechanic)
        mechanics = db.paginate(query, page=page, per_page=per_page)
        return mechanics_schema.jsonify(mechanics.items), 200
    except Exception as e:
        return handle_error("An error occurred while fetching mechanics", 500, str(e))


@mechanics_bp.route("/", methods=["POST"])
@limiter.limit("13 per hour")
def create_mechanic():
    try:
        new_mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return handle_error("Invalid input", 400, e.messages)

    name = new_mechanic_data.get("name")
    email = new_mechanic_data.get("email")
    existing_mechanic = db.session.execute(
        select(Mechanic).where(
            (Mechanic.name == name) | (Mechanic.email == email)
        )
    ).scalars().first()

    if existing_mechanic:
        return handle_error("A mechanic with the same name or email already exists", 409)

    if name and not email:
        email = f"{name.lower().replace(' ', '.')}@mechanicshop.com"
        new_mechanic_data["email"] = email

    try:
        new_mechanic = Mechanic(**new_mechanic_data)
        db.session.add(new_mechanic)
        db.session.commit()
        return mechanic_schema.jsonify(new_mechanic), 201
    except Exception as e:
        return handle_error("An error occurred while creating the mechanic", 500, str(e))


@mechanics_bp.route("/<int:mechanic_id>", methods=['DELETE'])
@limiter.limit("13 per hour")
def delete_mechanic(mechanic_id):
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic_instance = db.session.execute(query).scalars().first()

    if not mechanic_instance:
        return handle_error("Mechanic not found", 404)

    try:
        db.session.delete(mechanic_instance)
        db.session.commit()
        return jsonify({"message": "Mechanic deleted successfully"}), 200
    except Exception as e:
        return handle_error("An error occurred while deleting the mechanic", 500, str(e))


@mechanics_bp.route("/<int:mechanic_id>", methods=["PUT"])
@limiter.limit("3 per hour")
def update_mechanic(mechanic_id):
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic_instance = db.session.execute(query).scalars().first()

    if not mechanic_instance:
        return handle_error("Mechanic not found", 404)

    try:
        updated_data = mechanic_schema.load(request.json, partial=True)
    except ValidationError as e:
        return handle_error("Invalid input", 400, e.messages)

    try:
        for key, value in updated_data.items():
            setattr(mechanic_instance, key, value)
        db.session.commit()
        return mechanic_schema.jsonify(mechanic_instance), 200
    except Exception as e:
        return handle_error("An error occurred while updating the mechanic", 500, str(e))


@mechanics_bp.route("/most-tickets", methods=['GET'])
def most_tickets():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    mechanics.sort(key=lambda mechanic: len(mechanic.assigned_service_tickets), reverse=True)
    return mechanics_schema.jsonify(mechanics), 200


@mechanics_bp.route("/search", methods=['GET'])
def search_mechanic():
    name = request.args.get("name")
    salary = request.args.get("salary", type=float)
    below = request.args.get("below", type=bool, default=False)

    query = select(Mechanic)

    if name:
        query = query.where(Mechanic.name.ilike(f"%{name}%"))

    if salary is not None:
        query = query.where(Mechanic.salary <= salary if below else Mechanic.salary >= salary)

    mechanics = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200