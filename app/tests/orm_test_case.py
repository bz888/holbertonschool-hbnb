import unittest

from flask import Flask

from extensions import bcrypt, db


class ORMTestCase(unittest.TestCase):
    """Run repository/facade tests in an isolated SQLAlchemy database."""

    def setUp(self):
        self.app = Flask(self.__class__.__name__)
        self.app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        db.init_app(self.app)
        bcrypt.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()
