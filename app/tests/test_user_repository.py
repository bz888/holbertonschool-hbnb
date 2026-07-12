from models.user import User
from persistence.user_repository import UserRepository
from tests.orm_test_case import ORMTestCase


class TestUserRepository(ORMTestCase):
    def test_add_get_and_find_by_email(self):
        repository = UserRepository()
        user = User(
            first_name="Samuel",
            last_name="Chen",
            email="samuel@example.com",
        )
        user.hash_password("password123")
        repository.add(user)

        self.assertIs(repository.get(user.id), user)
        self.assertIs(
            repository.get_user_by_email("samuel@example.com"),
            user,
        )
        self.assertTrue(user.verify_password("password123"))
