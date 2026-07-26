import os
from pathlib import Path

from flask import Flask, request
from flask_restx import Api
from sqlalchemy import text


import config
from extensions import bcrypt, jwt, db

from api.errors import register_error_handlers
from api.v1.amenities import api as amenities_ns
from api.v1.auth import api as auth_ns
from api.v1.places import api as places_ns
from api.v1.reviews import api as reviews_ns
from api.v1.users import api as users_ns


SEED_SQL_DIRECTORY = Path(__file__).with_name("seeds")
SEED_SQL_FILES = {
    "sqlite": SEED_SQL_DIRECTORY / "seed.sqlite.sql",
    "mysql": SEED_SQL_DIRECTORY / "seed.mysql.sql",
}


def seed_database():
    """Apply idempotent seed data for the active database dialect."""
    dialect = db.engine.dialect.name
    seed_path = SEED_SQL_FILES.get(dialect)

    if seed_path is None:
        raise RuntimeError(f"Unsupported database dialect: {dialect}")

    statements = [
        statement.strip()
        for statement in seed_path.read_text(encoding="utf-8").split(";")
        if statement.strip()
    ]
    with db.engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def create_app(config_class=None):
    if config_class is None:
        environment = os.getenv("APP_ENV", "development").lower()

        try:
            config_class = config.config[environment]
        except KeyError as error:
            raise RuntimeError(
                f"Unsupported APP_ENV: {environment}"
            ) from error

    app = Flask(__name__)
    app.config.from_object(config_class)

    @app.after_request
    def allow_local_client(response):
        """Allow the locally served frontend to call either API mode."""
        origin = request.headers.get("Origin")
        is_local_origin = origin == "null" or (
            origin is not None
            and (
                origin.startswith("http://localhost:")
                or origin.startswith("http://127.0.0.1:")
            )
        )

        if app.config.get("ALLOW_LOCAL_CLIENT") and is_local_origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization"
            )
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, DELETE, OPTIONS"
            )
            response.headers["Vary"] = "Origin"

        return response

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        # schema.sql drops and recreates SQLite tables, so it is for manual
        # database resets only. The ORM safely creates any missing tables.
        db.create_all()
        seed_database()

    api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API', doc='/api/v1/')
    register_error_handlers(api)

    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')

    return app
