from flask import jsonify, request
from . import serviceTicket_bp
from app.models import ServiceStatus
from .schemas import service_ticket_schema, service_tickets_schema, return_service_ticket_schema, edit_ticket_schema
from app.models import db, Mechanic, ServiceTicket, Customer
from sqlalchemy import select, delete
from marshmallow import ValidationError
from app.extensions import cache


@serviceTicket_bp.route("/", methods=["POST"])
def create_service_ticket():
    try:
        if not request.json:
            return jsonify({"message": "Request body must be JSON"}), 400

        service_ticket_data = service_ticket_schema.load(request.json)
        print(service_ticket_data)

        # Check for missing required fields
        required_fields = ["vin", "service_date", "service_description", "customer_id"]
        for field in required_fields:
            if field not in service_ticket_data or not service_ticket_data[field]:
                return jsonify({"message": f"Missing or empty required field: {field}"}), 400

    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": e.messages}), 400
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

    try:
        # Cache the customer query to avoid redundant database hits
        @cache.cached(timeout=300, key_prefix=lambda: f"customer_{service_ticket_data['customer_id']}")
        def get_customer(customer_id):
            customer_query = select(Customer).where(Customer.id == customer_id)
            return db.session.execute(customer_query).scalar()

        customer = get_customer(service_ticket_data["customer_id"])
        if not customer:
            return jsonify({"message": f"Invalid customer ID: {service_ticket_data['customer_id']}"}), 400

        new_service_ticket = ServiceTicket(
            vin=service_ticket_data['vin'],
            service_date=service_ticket_data['service_date'],
            service_description=service_ticket_data['service_description'],
            customer_id=service_ticket_data["customer_id"]
        )

        for mechanic_id in service_ticket_data["mechanic_ids"]:
            # Cache the mechanic query to avoid redundant database hits
            @cache.cached(timeout=300, key_prefix=lambda: f"mechanic_{mechanic_id}")
            def get_mechanic(mechanic_id):
                query = select(Mechanic).where(Mechanic.id == mechanic_id)
                return db.session.execute(query).scalar()

            mechanic = get_mechanic(mechanic_id)
            if mechanic:
                new_service_ticket.mechanics.append(mechanic)
            else:
                return jsonify({"message": f"Invalid mechanic ID: {mechanic_id}"}), 400

        db.session.add(new_service_ticket)
        db.session.commit()
    except KeyError as e:
        return jsonify({"message": f"Missing required field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"message": "An error occurred while creating the service ticket", "error": str(e)}), 500

    return return_service_ticket_schema.jsonify(new_service_ticket), 201


@serviceTicket_bp.route("/", methods=["GET"])
# @cache.cached(timeout=60)
def get_all_tickets():
    try:
        # Pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        # Filtering
        mechanic_id = request.args.get("mechanic_id", type=int)
        service_state = request.args.get("status", type=str)  # Expecting a string for status

        # Build the query
        query = select(ServiceTicket)

        # Apply filtering for mechanic_id
        if mechanic_id:
            query = query.where(ServiceTicket.mechanics.any(Mechanic.id == mechanic_id))

        # Apply filtering for service_state
        if service_state:
            try:
                service_state_enum = ServiceStatus[service_state.upper()]  # Convert to enum
                query = query.where(ServiceTicket.status == service_state_enum)
            except KeyError:
                return jsonify({"message": f"Invalid status: {service_state}. Valid statuses are: {[status.name for status in ServiceStatus]}"}), 400

        # Apply pagination
        query = query.limit(per_page).offset((page - 1) * per_page)
        service_tickets = db.session.execute(query).scalars().all()

        return service_tickets_schema.jsonify(service_tickets), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while fetching service tickets", "error": str(e)}), 500
    

@serviceTicket_bp.route("/ticket-update/<int:ticket_id>", methods=["PUT"], strict_slashes=False)
def update_ticket_status(ticket_id):
    try:
        # Fetch the service ticket from the database
        query = select(ServiceTicket).where(ServiceTicket.id == ticket_id)
        service_ticket = db.session.execute(query).scalar_one_or_none()

        if not service_ticket:
            return jsonify({"message": f"Service ticket with ID {ticket_id} not found"}), 404

        # Get the new status from the request body
        data = request.get_json(silent=True)
        if not data or "status" not in data:
            return jsonify({"message": "Request body must include a 'status' field"}), 400

        new_status = data["status"]

        # Validate the new status
        valid_statuses = [status.value for status in ServiceStatus]
        if new_status not in valid_statuses:
            return jsonify({"message": f"Invalid status. Valid statuses are: {valid_statuses}"}), 400

        # Update the status of the service ticket
        try:
            service_ticket.status = ServiceStatus(new_status)
            db.session.commit()
            # Clear cache if necessary
            cache.delete(f"ticket_{ticket_id}")
        except Exception as e:
            db.session.rollback()
            raise e

        return jsonify({"message": f"Service ticket {ticket_id} status updated to {new_status}"}), 200

    except Exception as e:
        return jsonify({"message": "An error occurred while updating the service ticket status", "error": str(e)}), 500
    
@serviceTicket_bp.route("/<int:ticket_id>", methods=['PUT'])
def edit_ticket(ticket_id):
    try:
        # Validate and load the request data
        ticket_edits = edit_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": e.messages}), 400
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred while validating the request data", "error": str(e)}), 500

    try:
        # Fetch the service ticket from the database
        query = select(ServiceTicket).where(ServiceTicket.id == ticket_id)
        service_ticket = db.session.execute(query).scalars().first()

        if not service_ticket:
            return jsonify({"message": f"Service ticket with ID {ticket_id} not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred while fetching the service ticket", "error": str(e)}), 500

    try:
        # Add mechanics to the service ticket
        for mechanic_id in ticket_edits.get('add_mechanic_ids', []):
            query = select(Mechanic).where(Mechanic.id == mechanic_id)
            mechanic = db.session.execute(query).scalars().first()

            if not mechanic:
                return jsonify({"message": f"Mechanic with ID {mechanic_id} not found"}), 404

            if mechanic not in service_ticket.mechanics:
                service_ticket.mechanics.append(mechanic)

        # Remove mechanics from the service ticket
        for mechanic_id in ticket_edits.get('remove_mechanic_ids', []):
            query = select(Mechanic).where(Mechanic.id == mechanic_id)
            mechanic = db.session.execute(query).scalars().first()

            if not mechanic:
                return jsonify({"message": f"Mechanic with ID {mechanic_id} not found"}), 404

            if mechanic in service_ticket.mechanics:
                service_ticket.mechanics.remove(mechanic)
    except Exception as e:
        return jsonify({"message": "An error occurred while updating mechanics for the service ticket", "error": str(e)}), 500

    try:
        # Commit the changes to the database
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while saving changes to the database", "error": str(e)}), 500

    return return_service_ticket_schema.jsonify(service_ticket)


@serviceTicket_bp.route("/<int:ticket_id>", methods=['GET'])
def get_service_ticket(ticket_id):
    ticket = ServiceTicket.query.get(ticket_id)
    if not ticket:
        return jsonify({'message': f'Service ticket with ID {ticket_id} not found'}), 404
    return return_service_ticket_schema.jsonify(ticket), 200


@serviceTicket_bp.route("/<int:ticket_id>", methods=['DELETE'])
def delete_service_ticket(ticket_id):
    ticket = ServiceTicket.query.get(ticket_id)
    if not ticket:
        return jsonify({'message': 'Service ticket not found'}), 404
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': f'Service ticket {ticket_id} deleted'}), 200