from pathlib import Path

from flask import Flask
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
SEED_ADMIN_ID = "36c9050e-ddd3-4c3b-9731-9f487208bbc1"
SEED_SQL_PATH = Path(__file__).with_name("seed.sql")


def seed_database():
    """Apply the SQL seed data once after the ORM has created its tables."""
    with db.engine.connect() as connection:
        already_seeded = connection.execute(
            text("SELECT 1 FROM users WHERE id = :id"),
            {"id": SEED_ADMIN_ID},
        ).scalar()

    if already_seeded:
        return

    statements = [
        statement.strip()
        for statement in SEED_SQL_PATH.read_text(encoding="utf-8").split(";")
        if statement.strip()
    ]
    with db.engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))



def create_app(config_class=config.DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

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
