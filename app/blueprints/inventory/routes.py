from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.schemas import inventory_schema, inventories_schema
from app.blueprints.service_tickets import serviceTicket_bp
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Inventory, ServiceTicket, ServiceTicketInventory, db
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import limiter
from sqlalchemy import select

# Utility function for error handling
def handle_error(e):
    if isinstance(e, ValidationError):
        return jsonify({"error": e.messages}), 400
    elif isinstance(e, SQLAlchemyError):
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return jsonify({"error": "An unexpected error occurred"}), 500

# Utility function for pagination
def paginate_items(items, page, per_page):
    start = (page - 1) * per_page
    end = start + per_page
    paginated_items = items[start:end]
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    return {
        "items": inventories_schema.dump(paginated_items),
        "page": page,
        "per_page": per_page,
        "total_items": total_items,
        "total_pages": total_pages
    }

# Utility function to build inventory query with filters
def build_inventory_query(min_price=None, max_price=None, name_filter=None, unassigned_only=False):
    query = select(Inventory)
    if min_price is not None:
        query = query.where(Inventory.price >= min_price)
    if max_price is not None:
        query = query.where(Inventory.price <= max_price)
    if name_filter:
        query = query.where(Inventory.name.ilike(f"%{name_filter}%"))
    if unassigned_only:
        query = query.where(~Inventory.id.in_(
            select(ServiceTicketInventory.inventory_id)
        ))
    return query

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
    except Exception as e:
        return handle_error(e)

# Route to delete an inventory item
@inventory_bp.route('/items/<int:item_id>', methods=['DELETE'])
@limiter.limit("5 per minute")
def delete_inventory_item(item_id):
    try:
        query = select(Inventory).where(Inventory.id == item_id)
        item = db.session.execute(query).scalars().first()

        if not item:
            return jsonify({"error": "Item not found"}), 404

        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deleted successfully"}), 200
    except Exception as e:
        return handle_error(e)

# Route to get inventory items
@inventory_bp.route('/items', methods=['GET'])
@limiter.limit("10 per minute")
def get_inventory_items():
    try:
        item_id = request.args.get('id', type=int)

        if item_id:
            query = select(Inventory).where(Inventory.id == item_id)
            item = db.session.execute(query).scalars().first()

            if not item:
                return jsonify({"error": "Item not found"}), 404

            return jsonify(inventory_schema.dump(item)), 200

        # Pagination and filters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        name_filter = request.args.get('name', type=str)
        unassigned_only = request.args.get('unassigned', type=bool, default=False)

        query = build_inventory_query(min_price, max_price, name_filter, unassigned_only)
        items = db.session.execute(query).scalars().all()

        return jsonify(paginate_items(items, page, per_page)), 200
    except Exception as e:
        return handle_error(e)

# Route to assign an inventory item to a service ticket
@inventory_bp.route('/assign-item/<int:inventory_id>', methods=['POST'])
@limiter.limit("5 per minute")
def assign_item_to_ticket(inventory_id):
    try:
        data = request.get_json()
        service_ticket_id = data.get("service_ticket_id")
        quantity = data.get("quantity", 1)

        if not service_ticket_id:
            return jsonify({"error": "service_ticket_id is required"}), 400

        service_ticket = db.session.get(ServiceTicket, service_ticket_id)
        inventory_item = db.session.get(Inventory, inventory_id)

        if not service_ticket or not inventory_item:
            return jsonify({"error": "Invalid service_ticket_id or inventory_id"}), 404

        association = ServiceTicketInventory(
            service_ticket_id=service_ticket_id,
            inventory_id=inventory_id,
            quantity=quantity
        )
        db.session.add(association)
        db.session.commit()
        return jsonify({"message": "Item assigned to service ticket successfully"}), 200
    except Exception as e:
        return handle_error(e)

# Route to update an inventory item
@inventory_bp.route('/items/<int:item_id>', methods=['PUT'])
@limiter.limit("5 per minute")
def update_inventory_item(item_id):
    try:
        data = request.get_json()
        item = db.session.get(Inventory, item_id)

        if not item:
            return jsonify({"error": "Item not found"}), 404

        if "name" in data:
            item.name = data["name"]
        if "price" in data:
            item.price = data["price"]

        db.session.commit()
        return jsonify({"message": "Item updated successfully", "item": inventory_schema.dump(item)}), 200
    except Exception as e:
        return handle_error(e)