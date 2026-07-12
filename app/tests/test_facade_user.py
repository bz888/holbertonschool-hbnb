from __init__ import create_app
from extensions import db
from services.facade import HBnBFacade


app = create_app()

with app.app_context():

    db.drop_all()
    db.create_all()

    facade = HBnBFacade()

    user = facade.create_user({
        "first_name": "Alice",
        "last_name": "Brown",
        "email": "alice@example.com",
        "password": "secret123"
    })

    print("Created:")
    print(user.id)
    print(user.email)


    found = facade.get_user(user.id)

    print("\nRetrieved:")
    print(found.first_name)
    print(found.email)


    found_email = facade.get_user_by_email(
        "alice@example.com"
    )

    print("\nBy email:")
    print(found_email.first_name)