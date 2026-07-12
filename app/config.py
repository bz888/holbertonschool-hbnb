import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    SEED_ADMIN = os.getenv('SEED_ADMIN', 'true').lower() == 'true'
    ADMIN_FIRST_NAME = os.getenv('ADMIN_FIRST_NAME', 'Admin')
    ADMIN_LAST_NAME = os.getenv('ADMIN_LAST_NAME', 'User')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin-password')
    DEBUG = False
    ERROR_INCLUDE_MESSAGE = False
    RESTX_ERROR_404_HELP = False


class DevelopmentConfig(Config):
    DEBUG = True
