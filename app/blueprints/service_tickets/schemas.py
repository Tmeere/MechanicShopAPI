from app.extensions import ma
from app.models import ServiceTicket
from marshmallow import fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = fields.Nested("MechanicSchema", many=True)  # Nested mechanics relationship
    customer = fields.Nested("CustomerSchema")  # Nested customer relationship

    class Meta:
        model = ServiceTicket
        fields = ("id", "vin", "service_date", "status", "service_description", "customer_id", "customer", "mechanics",  "mechanic_ids")
        load_instance = False 

class EditTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=False)
    remove_mechanic_ids = fields.List(fields.Int(), required=False)

    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids")
    
# Single and multiple schemas
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
return_service_ticket_schema = ServiceTicketSchema(exclude=["customer_id"])
edit_ticket_schema = EditTicketSchema()