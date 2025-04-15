from app.models import Customer
from app.extensions import ma
from marshmallow import Schema, fields

# Customer Schema
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    name = fields.String(required=True)
    email = fields.Email(required=True)
    phone = fields.String(required=True)
    class Meta:
        model = Customer  

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)


