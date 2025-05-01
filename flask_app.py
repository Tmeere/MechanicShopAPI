from app import create_app
from app.models import db

# Create the Flask app
app = create_app('ProductionConfig')

# Initialize the database
with app.app_context():
    # db.drop_all()
    db.create_all()
    
# app.run()
