

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:123mysql@localhost/mechanicShop_db'
    DEBUG = True
    CACHE_TYPE = "SimpleCache"
    
    
class TestingConfig:
    pass

class ProductionConfig:
    pass
