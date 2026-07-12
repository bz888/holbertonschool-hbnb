from services.facade import HBnBFacade
from tests.orm_test_case import ORMTestCase


class TestFacadeUserRepositoryIntegration(ORMTestCase):
    def test_create_and_retrieve_user(self):
        facade = HBnBFacade()
        user = facade.create_user(
            {
                "first_name": "Alice",
                "last_name": "Brown",
                "email": "alice@example.com",
                "password": "secret123",
            },
            is_admin=True,
        )

        self.assertIs(facade.get_user(user.id), user)
        self.assertIs(
            facade.get_user_by_email("alice@example.com"),
            user,
        )
