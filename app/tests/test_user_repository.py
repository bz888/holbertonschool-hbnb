from __init__ import create_app
from extensions import db
from models.user import User
from persistence.user_repository import UserRepository


app = create_app()


with app.app_context():

    db.drop_all()
    db.create_all()

    repo = UserRepository()

    # Create user
    user = User(
        first_name="Samuel",
        last_name="Chen",
        email="samuel@example.com"
    )

    user.hash_password("password123")

    repo.add(user)

    print("Created user:")
    print(user.id)
    print(user.email)


    # Find by ID
    found = repo.get(user.id)

    print("\nFound by ID:")
    print(found.first_name)
    print(found.email)


    # Find by email
    found_email = repo.get_user_by_email(
        "samuel@example.com"
    )

    print("\nFound by email:")
    print(found_email.first_name)
    print(found_email.email)


    # Verify password
    print(
        "\nPassword valid:",
        found_email.verify_password("password123")
    )