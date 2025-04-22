from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.schemas import inventory_schema, inventories_schema
from app.blueprints.service_tickets import serviceTicket_bp
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Inventory, ServiceTicket, ServiceTicketInventory, db  # Added missing imports
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import limiter
from sqlalchemy import select  # Ensure this import is present

# Route to create a new inventory item
@inventory_bp.route('/items', methods=['POST'])
@limiter.limit("5 per minute")
def create_inventory_item():
    try:
        data = request.get_json()
        new_item = Inventory(
            name=data['name'],
            price=data['price']
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify(inventory_schema.dump(new_item)), 201
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

# Route to delete an inventory item
@inventory_bp.route('/items/<int:item_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
def delete_inventory_item(item_id):
    try:
        # Corrected variable name
        query = select(Inventory).where(Inventory.id == item_id)
        item = db.session.execute(query).scalars().first()  # Corrected variable name

        # Check if the item exists
        if not item:
            return jsonify({"error": "Item not found"}), 404

        # Delete the item
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deleted successfully"}), 200
    except SQLAlchemyError as e:
        # Handle database errors
        return jsonify({"error": str(e)}), 500
    

# Route to get inventory items
@inventory_bp.route('/items', methods=['GET'])
@limiter.limit("10 per minute")
def get_inventory_items():
    try:
        # Check if an item ID is provided as a query parameter
        item_id = request.args.get('id', type=int)

        if item_id:
            # Fetch a specific inventory item by ID
            query = select(Inventory).where(Inventory.id == item_id)
            item = db.session.execute(query).scalars().first()

            if not item:
                return jsonify({"error": "Item not found"}), 404

            return jsonify(inventory_schema.dump(item)), 200
        else:
            # Pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            # Filters
            min_price = request.args.get('min_price', type=float)
            max_price = request.args.get('max_price', type=float)
            name_filter = request.args.get('name', type=str)
            unassigned_only = request.args.get('unassigned', type=bool, default=False)

            # Build query with filters
            query = select(Inventory)
            if min_price is not None:
                query = query.where(Inventory.price >= min_price)
            if max_price is not None:
                query = query.where(Inventory.price <= max_price)
            if name_filter:
                query = query.where(Inventory.name.ilike(f"%{name_filter}%"))
            if unassigned_only:
                # Filter for items not assigned to any service ticket
                query = query.where(~Inventory.id.in_(
                    select(ServiceTicketInventory.inventory_id)
                ))

            # Fetch filtered inventory items
            items = db.session.execute(query).scalars().all()

            # Apply pagination
            start = (page - 1) * per_page
            end = start + per_page
            paginated_items = items[start:end]

            return jsonify({
                "items": inventories_schema.dump(paginated_items),
                "page": page,
                "per_page": per_page,
                "total_items": len(items),
                "total_pages": (len(items) + per_page - 1) // per_page
            }), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500


@inventory_bp.route('/assign-item/<int:inventory_id>', methods=['POST'])
@limiter.limit("5 per minute")
def assign_item_to_ticket(inventory_id):
    try:
        # Get data from the request
        data = request.get_json()
        print("Request data:", data)

        service_ticket_id = data.get("service_ticket_id")
        quantity = data.get("quantity", 1)  

        # Validate input
        if not service_ticket_id:
            return jsonify({"error": "service_ticket_id is required"}), 400

        # Fetch the service ticket and inventory item
        service_ticket = db.session.get(ServiceTicket, service_ticket_id)
        inventory_item = db.session.get(Inventory, inventory_id)

        if not service_ticket:
            return jsonify({"error": "Service ticket not found"}), 404
        if not inventory_item:
            return jsonify({"error": "Inventory item not found or invalid inventory_id"}), 404

        # Create a new ServiceTicketInventory entry
        association = ServiceTicketInventory(
            service_ticket_id=service_ticket_id,
            inventory_id=inventory_id,
            quantity=quantity
        )
        db.session.add(association)
        db.session.commit()

        return jsonify({"message": "Item assigned to service ticket successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()  
        return jsonify({"error": str(e)}), 500


@inventory_bp.route('/items/<int:item_id>', methods=['PUT'])
@limiter.limit("5 per minute")
def update_inventory_item(item_id):
    try:
        # Get the request data
        data = request.get_json()

        # Fetch the inventory item by ID
        item = db.session.get(Inventory, item_id)

        # Check if the item exists
        if not item:
            return jsonify({"error": "Item not found"}), 404

        # Update the item's attributes
        if "name" in data:
            item.name = data["name"]
        if "price" in data:
            item.price = data["price"]

        # Commit the changes to the database
        db.session.commit()

        return jsonify({"message": "Item updated successfully", "item": inventory_schema.dump(item)}), 200
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500