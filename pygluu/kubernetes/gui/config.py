import os
import secrets

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "supersecret"
    UPLOAD_FOLDER = "/"
    ALLOWED_EXTENSIONS = {"crt", "yaml"}


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    SECRET_KEY = secrets.token_urlsafe(32)


class TestingConfig(Config):
    TESTING = True
