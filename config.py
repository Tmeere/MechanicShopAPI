

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:123mysql@localhost/mechanicShop_db'
    DEBUG = True
    
class TestingConfig:
    pass

class ProductionConfig:
    pass
