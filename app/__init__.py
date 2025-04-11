from flask import Flask
from app.models import db
from app.extensions import ma
from app.blueprints.customers import members_bp


def create_app(config_name):
    
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')
    
    
    db.init_app(app)
    ma.init_app(app)
    
    
    app.register_blueprint(members_bp, url_prefix='/customers')
    
    return app 

#  Sets what mode our app is in 
# app = create_app('DevelopmentConfig')