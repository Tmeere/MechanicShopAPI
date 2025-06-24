import os

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:123mysql@localhost/mechanicShop_db'
    DEBUG = True
    CACHE_TYPE = "SimpleCache"
    
class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    DEBUG = True
    CACHE_TYPE = 'SimpleCache'
    
class ProductionConfig:
    # Get database URL from environment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Fix Heroku/Render postgres:// URLs to postgresql://
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    # If no DATABASE_URL is provided, use a fallback (though this shouldn't happen in production)
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///fallback.db'
        print("WARNING: No DATABASE_URL found, using SQLite fallback")
    
    CACHE_TYPE = "SimpleCache"
    DEBUG = False
    
    # PostgreSQL-specific engine options
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,          # Verify connections before use
        'pool_recycle': 300,            # Recycle connections every 5 minutes
        'pool_timeout': 20,             # Timeout after 20 seconds
        'max_overflow': 0,              # Don't allow overflow connections
        'connect_args': {
            'sslmode': 'require',       # Require SSL connection
            'connect_timeout': 30,      # Connection timeout
            'application_name': 'MechanicShopAPI'  # App name for monitoring
        }
    }
    
