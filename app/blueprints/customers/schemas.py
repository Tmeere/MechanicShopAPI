from app.models import Customer,  ServiceTicket, Mechanic
from app.extensions import ma
from marshmallow import Schema, fields

# Customer Schema
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    name = fields.String(required=True)
    email = fields.Email(required=True)
    phone = fields.String(required=True)
    class Meta:
        model = Customer  # Use `Customer` model

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

# ServiceTicket Schema
class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket  # Use `ServiceTicket` model

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)

# Mechanic Schema
class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic  # Use `Mechanic` model

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)


