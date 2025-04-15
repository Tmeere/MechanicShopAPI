from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Mechanic, db
from sqlalchemy import select
from app.extensions import limiter, cache


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
@cache.cached(timeout=60)  # Cache for 1 minute
def get_all_mechanics():
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