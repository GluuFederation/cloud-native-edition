class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "supersecret"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    SECRET_KEY = ""


class TestingConfig(Config):
    TESTING = True
