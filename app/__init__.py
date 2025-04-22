from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
from app.models import db
from app.extensions import ma, limiter, cache
from app.blueprints.customers import customers_bp
from app.blueprints.service_tickets import serviceTicket_bp
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.inventory import inventory_bp

# Swagger configuration
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI
API_URL = '/static/swagger.yaml'  # Path to the Swagger YAML file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Mechanic Shop Management System"
    }
)

def create_app(config_name):
    # Create the Flask application
    app = Flask(__name__)
    
    # Load configuration from the specified config class
    app.config.from_object(f'config.{config_name}')
    
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    # Register blueprints with their respective URL prefixes
    app.register_blueprint(customers_bp, url_prefix='/customers') 
    app.register_blueprint(inventory_bp, url_prefix='/inventory') 
    app.register_blueprint(serviceTicket_bp, url_prefix='/service_ticket')   
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)  # Register Swagger UI blueprint
    
    return app