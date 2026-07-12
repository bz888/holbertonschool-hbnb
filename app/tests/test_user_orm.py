from flask import Flask

from extensions import db, bcrypt
from models.user import User


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

db.init_app(app)
bcrypt.init_app(app)


with app.app_context():

    db.create_all()

    user = User(
        first_name="John",
        last_name="Smith",
        email="john@example.com"
    )

    user.hash_password("password123")

    db.session.add(user)
    db.session.commit()

    print("ID:", user.id)
    print("Name:", user.first_name, user.last_name)
    print("Email:", user.email)
    print("Password valid:",
          user.verify_password("password123"))