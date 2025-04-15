from app.extensions import ma
from app.models import Mechanic
from marshmallow import fields

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    name = fields.String(required=True)
    email = fields.Email(required=False)
    salary = fields.Float(required=True, validate=lambda x: x > 0)

    class Meta:
        model = Mechanic  # Use `Mechanic` model

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)





