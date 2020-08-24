import os


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "supersecret"
    UPLOAD_FOLDER = "/"
    ALLOWED_EXTENSIONS = {"crt", "yaml"}


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    SECRET_KEY = os.environ.get("SECRET_KEY")


class TestingConfig(Config):
    TESTING = True
