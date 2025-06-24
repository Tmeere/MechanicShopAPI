from app import create_app
from app.models import db
import os

# Create the Flask app
# Use ProductionConfig for deployment, TestingConfig for local testing
config_name = os.environ.get('FLASK_ENV', 'ProductionConfig')
app = create_app(config_name)


# Initialize the database
with app.app_context():
    try:
        # Only create tables if they don't exist (safer for production)
        db.create_all()
        print("✅ Database tables initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Don't exit in production, let the app start anyway
        pass
    
# app.run()
