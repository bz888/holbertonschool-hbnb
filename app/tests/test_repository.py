import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.user import User
from persistence.repository import InMemoryRepository


class TestInMemoryRepository(unittest.TestCase):
    def setUp(self):
        self.repository = InMemoryRepository()
        self.active_user = self.repository.add(
            User(
                "Ada",
                "Lovelace",
                "ada@example.com",
            )
        )
        self.inactive_user = self.repository.add(
            User(
                "Grace",
                "Hopper",
                "grace@example.com",
                is_active=False,
            )
        )

    def test_find_one_returns_first_matching_object(self):
        user = self.repository.find_one(
            email="ada@example.com",
            is_active=True,
        )

        self.assertIs(user, self.active_user)

    def test_find_one_returns_none_when_no_object_matches(self):
        user = self.repository.find_one(
            email="missing@example.com",
        )

        self.assertIsNone(user)

    def test_find_all_filters_by_multiple_attributes(self):
        users = self.repository.find_all(is_active=False)

        self.assertEqual(users, [self.inactive_user])

    def test_find_all_without_filters_returns_every_object(self):
        users = self.repository.find_all()

        self.assertEqual(
            users,
            [self.active_user, self.inactive_user],
        )

    def test_find_all_does_not_match_missing_attributes(self):
        users = self.repository.find_all(missing=None)

        self.assertEqual(users, [])

    def test_get_by_attribute_uses_dynamic_lookup(self):
        user = self.repository.get_by_attribute(
            "email",
            "grace@example.com",
        )

        self.assertIs(user, self.inactive_user)


if __name__ == "__main__":
    unittest.main()
