from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models.base_model import Base
from models.user import User


engine = create_engine(
    "sqlite:///:memory:",
    echo=True,
)

Base.metadata.create_all(engine)


with Session(engine) as session:
    user = User(
        first_name=" John ",
        last_name=" Smith ",
        email=" JOHN@EXAMPLE.COM ",
    )

    user.hash_password("mypassword")

    session.add(user)
    session.commit()

    print("ID:", user.id)
    print("Name:", user.first_name, user.last_name)
    print("Email:", user.email)
    print("Password:", user.password)
    print("Created:", user.created_at)
    print("Updated:", user.updated_at)

    print(
        "Password valid:",
        user.verify_password("mypassword")
    )