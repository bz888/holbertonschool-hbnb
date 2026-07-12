from flask import Flask
from flask_restx import Api


import config
from extensions import bcrypt, jwt, db

from api.errors import register_error_handlers
from api.v1.amenities import api as amenities_ns
from api.v1.auth import api as auth_ns
from api.v1.places import api as places_ns
from api.v1.reviews import api as reviews_ns
from api.v1.users import api as users_ns
from services import facade


def seed_admin(app):
    """Create the configured initial administrator when none exists."""
    if not app.config.get('SEED_ADMIN', True):
        return None

    email = app.config['ADMIN_EMAIL']
    existing_admin = facade.get_user_by_email(email)
    if existing_admin is not None:
        return existing_admin

    return facade.create_user(
        {
            'first_name': app.config['ADMIN_FIRST_NAME'],
            'last_name': app.config['ADMIN_LAST_NAME'],
            'email': email,
            'password': app.config['ADMIN_PASSWORD'],
            'is_admin': True,
        },
        is_admin=True,
    )



def create_app(config_class=config.DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        # The admin seed queries the users table, so initialise the schema
        # before attempting to read from it on a fresh installation.
        db.create_all()
        print("Database tables created:")
        print(db.metadata.tables.keys())
        seed_admin(app)

    api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API', doc='/api/v1/')
    register_error_handlers(api)

    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')

    return app
