from flask import jsonify, request
from . import serviceTicket_bp
from .schemas import service_ticket_schema, service_tickets_schema, return_service_ticket_schema
from app.models import db, Mechanic, ServiceTicket, Customer  # Ensure Customer is imported
from sqlalchemy import select, delete
from marshmallow import ValidationError


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
        # Check if the customer_id is valid
        customer_query = select(Customer).where(Customer.id == service_ticket_data["customer_id"])
        customer = db.session.execute(customer_query).scalar()
        if not customer:
            return jsonify({"message": f"Invalid customer ID: {service_ticket_data['customer_id']}"}), 400

        new_service_ticket = ServiceTicket(
            vin=service_ticket_data['vin'],
            service_date=service_ticket_data['service_date'],
            service_description=service_ticket_data['service_description'],
            customer_id=service_ticket_data["customer_id"]
        )

        for mechanic_id in service_ticket_data["mechanic_ids"]:
            query = select(Mechanic).where(Mechanic.id == mechanic_id)
            mechanic = db.session.execute(query).scalar()
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
def get_all_tickets():
    try:
        # Query all service tickets
        query = select(ServiceTicket)
        service_tickets = db.session.execute(query).scalars().all()

        # Return the serialized list of service tickets
        return service_tickets_schema.jsonify(service_tickets), 200
    except Exception as e:
        return jsonify({"message": "An error occurred while fetching service tickets", "error": str(e)}), 500