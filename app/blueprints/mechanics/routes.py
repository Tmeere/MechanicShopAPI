from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Mechanic, db, ServiceTicket
from sqlalchemy import select
from app.utils.util import encode_token, token_required
from app.extensions import limiter, cache


@mechanics_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = request.json
        email = credentials['email']
        name = credentials['name']
    except KeyError:
        return jsonify({'message': 'Invalid payload, expecting email and name'}), 400

    query = select(Mechanic).where(Mechanic.email == email)
    mechanic = db.session.execute(query).scalar_one_or_none()
    
    if not mechanic:
        return jsonify({'message': 'Email invalid or User does not exist, create an account?'})

    if mechanic and mechanic.name == name:
        auth_token = encode_token(mechanic.id)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'message': "Invalid email or name"}), 401

@mechanics_bp.route("/remove-ticket/<int:ticket_id>", methods=["DELETE"])
@token_required
def remove_ticket(mechanic_id, ticket_id):
    # Ensure the mechanic is logged in (mechanic_id is provided by @token_required)
    if not mechanic_id:
        return jsonify({"message": "Unauthorized. Please log in."}), 401

    # Query the service ticket by its ID and ensure it belongs to the mechanic
    query = select(ServiceTicket).where(
        ServiceTicket.id == ticket_id, 
        ServiceTicket.mechanics.any(id=mechanic_id)
    )
    ticket = db.session.execute(query).scalars().first()

    # Check if the ticket exists and belongs to the mechanic
    if ticket is None:
        return jsonify({"message": "Ticket not found or you are not authorized to delete this ticket"}), 404

    # Delete the ticket from the database
    db.session.delete(ticket)
    db.session.commit()

    # Return a success message
    return jsonify({"message": f"Ticket with ID {ticket_id} successfully deleted"}), 200
    
@mechanics_bp.route("/<int:mechanic_id>", methods=['GET'])
@limiter.limit("10 per minute")  # Limit to 10 requests per minute
@cache.cached(timeout=60, key_prefix=lambda: f"mechanic_{mechanic_id}")  # Cache for 1 minute
def get_mechanic(mechanic_id):
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic_instance = db.session.execute(query).scalars().first()
    
    if mechanic_instance is None:
        # Return a 404 error if the mechanic is not found
        return jsonify({"error": "Mechanic not found"}), 404

    # Return the mechanic as a response
    return mechanic_schema.jsonify(mechanic_instance), 200


@mechanics_bp.route("/", methods=['GET'])
@limiter.limit("10 per minute")  # Limit to 10 requests per minute
# @cache.cached(timeout=60)  # Cache for 1 minute
def get_all_mechanics():
    
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Mechanic)
        mechnics = db.paginate(query, page=page, per_page=per_page)
        
        return mechanics_schema.jsonify(mechnics),200
    except:
        
        query = select(Mechanic)
        mechanics = db.session.execute(query).scalars().all()

        # Return all mechanics as a response
        return mechanics_schema.jsonify(mechanics), 200


@mechanics_bp.route("/", methods=["POST"])
@limiter.limit("3 per hour")  # Limit to 3 requests per hour
def create_mechanic():
    try:
        # Validate and deserialize input data
        new_mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as validation_error:
        # Return validation errors
        return jsonify({"error": "Invalid input", "details": validation_error.messages}), 400

    # Automatically generate an email based on the name
    name = new_mechanic_data.get("name")
    if name:
        email = f"{name.lower().replace(' ', '.')}@example.com"
        new_mechanic_data["email"] = email

    # Create a new mechanic instance
    new_mechanic = Mechanic(**new_mechanic_data)

    # Add the new mechanic to the database
    db.session.add(new_mechanic)
    db.session.commit()

    # Return the newly created mechanic as a response
    return mechanic_schema.jsonify(new_mechanic), 201


@mechanics_bp.route("/<int:mechanic_id>", methods=['DELETE'])
@limiter.limit("3 per hour")  # Limit to 3 requests per hour
def delete_mechanic(mechanic_id):
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic_instance = db.session.execute(query).scalars().first()
    
    if mechanic_instance is None:
        # Return a 404 error if the mechanic is not found
        return jsonify({"error": "Mechanic not found"}), 404

    # Delete the mechanic from the database
    db.session.delete(mechanic_instance)
    db.session.commit()

    # Return a success message
    return jsonify({"message": "Mechanic deleted successfully"}), 200


@mechanics_bp.route("/<int:mechanic_id>", methods=["PUT"])
@limiter.limit("3 per hour")  # Limit to 3 requests per hour
def update_mechanic(mechanic_id):
    # Fetch the mechanic instance from the database
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic_instance = db.session.execute(query).scalars().first()

    if mechanic_instance is None:
        # Return a 404 error if the mechanic is not found
        return jsonify({"error": "Mechanic not found"}), 404

    try:
        # Validate and deserialize input data
        updated_data = mechanic_schema.load(request.json, partial=True)
    except ValidationError as validation_error:
        # Return validation errors
        return jsonify({"error": "Invalid input", "details": validation_error.messages}), 400

    # Update the mechanic instance with the new data
    for key, value in updated_data.items():
        setattr(mechanic_instance, key, value)

    # Commit the changes to the database
    db.session.commit()

    # Return the updated mechanic as a response
    return mechanic_schema.jsonify(mechanic_instance), 200

@mechanics_bp.route("/most-tickets", methods=['GET'])
def most_tickets():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    # Sort mechanics by the number of assigned service tickets in descending order
    mechanics.sort(key=lambda mechanic: len(mechanic.assigned_service_tickets), reverse=True)

    # Return the sorted mechanics as a response
    return mechanics_schema.jsonify(mechanics)
    
@mechanics_bp.route("/search", methods=['GET'])
def search_mechanic():
    name = request.args.get("name")
    salary = request.args.get("salary", type=float)
    below = request.args.get("below", type=bool, default=False) 

    # Build the query
    query = select(Mechanic)

    # Apply name filter if provided
    if name:
        query = query.where(Mechanic.name.like(f'%{name}%'))

    # Apply salary filter if provided
    if salary:
        if below:
            query = query.where(Mechanic.salary <= salary)
        else:
            query = query.where(Mechanic.salary >= salary) 

    # Execute the query
    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics)