from flask import Flask
from flask_restx import Api

import config
from extensions import bcrypt, jwt

from api.errors import register_error_handlers
from api.v1.amenities import api as amenities_ns
from api.v1.auth import api as auth_ns
from api.v1.places import api as places_ns
from api.v1.reviews import api as reviews_ns
from api.v1.users import api as users_ns


def create_app(config_class=config.DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    bcrypt.init_app(app)
    jwt.init_app(app)

    api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API', doc='/api/v1/')
    register_error_handlers(api)

    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')

    return app
