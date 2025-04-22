from app.extensions import ma
from app.models import Inventory

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        fields = ("id", "name", "price")

# Single and multiple schemas for Inventory
inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)




