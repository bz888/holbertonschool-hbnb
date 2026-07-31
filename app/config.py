import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    DEBUG = False
    ERROR_INCLUDE_MESSAGE = False
    RESTX_ERROR_404_HELP = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOW_LOCAL_CLIENT = False


class DevelopmentConfig(Config):
    DEBUG = True
    ALLOW_LOCAL_CLIENT = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(basedir, "..", "development.db"),
    )


class ProductionConfig(Config):
    """Local MySQL configuration used to verify dialect compatibility."""

    ALLOW_LOCAL_CLIENT = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
