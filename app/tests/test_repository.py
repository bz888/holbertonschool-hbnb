import sys
import unittest
from pathlib import Path

from sqlalchemy.exc import InvalidRequestError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.user import User
from persistence.repository import SQLAlchemyRepository
from tests.orm_test_case import ORMTestCase


class TestSQLAlchemyRepository(ORMTestCase):
    def setUp(self):
        super().setUp()
        self.repository = SQLAlchemyRepository(User)
        self.active_user = self.repository.add(
            User(
                "Ada",
                "Lovelace",
                "ada@example.com",
                password="password-hash",
            )
        )
        self.inactive_user = self.repository.add(
            User(
                "Grace",
                "Hopper",
                "grace@example.com",
                password="password-hash",
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
        with self.assertRaises(InvalidRequestError):
            self.repository.find_all(missing=None)

    def test_get_by_attribute_uses_dynamic_lookup(self):
        user = self.repository.get_by_attribute(
            "email",
            "grace@example.com",
        )

        self.assertIs(user, self.inactive_user)


if __name__ == "__main__":
    unittest.main()
