from extensions import db
from models.user import User
from tests.orm_test_case import ORMTestCase


class TestUserORM(ORMTestCase):
    def test_user_round_trip_and_password_verification(self):
        user = User(
            first_name="John",
            last_name="Smith",
            email="john@example.com",
        )
        user.hash_password("password123")
        db.session.add(user)
        db.session.commit()

        stored_user = db.session.get(User, user.id)
        self.assertEqual(stored_user.email, "john@example.com")
        self.assertTrue(stored_user.verify_password("password123"))
