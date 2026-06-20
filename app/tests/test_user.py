import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.user import User
from services.facade import HBnBFacade
from utils.errors.user import EmailAlreadyRegistered, UserNotFound


class TestUser(unittest.TestCase):
    def test_create_valid_user(self):
        user = User("Ada", "Lovelace", "ada@example.com")

        self.assertEqual(user.first_name, "Ada")
        self.assertEqual(user.last_name, "Lovelace")
        self.assertEqual(user.email, "ada@example.com")
        self.assertFalse(user.is_admin)
        self.assertTrue(user.is_active)
        self.assertEqual(user.places, [])
        self.assertEqual(user.reviews, [])

    def test_user_trims_valid_string_fields(self):
        user = User(
            "  Ada  ",
            "  Lovelace  ",
            "  ADA@EXAMPLE.COM  ",
        )

        self.assertEqual(user.first_name, "Ada")
        self.assertEqual(user.last_name, "Lovelace")
        self.assertEqual(user.email, "ada@example.com")

    def test_user_rejects_empty_names(self):
        for first_name, last_name in (
            ("", "Lovelace"),
            ("Ada", "   "),
        ):
            with self.subTest(
                first_name=first_name,
                last_name=last_name,
            ):
                with self.assertRaises(ValueError):
                    User(
                        first_name,
                        last_name,
                        "ada@example.com",
                    )

    def test_user_rejects_names_longer_than_50_characters(self):
        with self.assertRaises(ValueError):
            User(
                "A" * 51,
                "Lovelace",
                "ada@example.com",
            )

        with self.assertRaises(ValueError):
            User(
                "Ada",
                "L" * 51,
                "ada@example.com",
            )

    def test_user_accepts_names_at_50_character_boundary(self):
        user = User(
            "A" * 50,
            "L" * 50,
            "ada@example.com",
        )

        self.assertEqual(len(user.first_name), 50)
        self.assertEqual(len(user.last_name), 50)

    def test_user_rejects_invalid_email_format(self):
        for email in (
            "",
            "invalid-email",
            "missing-domain@",
            "@missing-user.com",
            "user@example",
            "user @example.com",
        ):
            with self.subTest(email=email):
                with self.assertRaises(ValueError):
                    User("Ada", "Lovelace", email)

    def test_user_update_uses_validation(self):
        user = User("Ada", "Lovelace", "ada@example.com")

        with self.assertRaises(ValueError):
            user.update({"email": "invalid-email"})

    def test_add_place(self):
        user = User("Ada", "Lovelace", "ada@example.com")
        place = object()

        user.add_place(place)

        self.assertEqual(user.places, [place])

    def test_add_review(self):
        user = User("Ada", "Lovelace", "ada@example.com")
        review = object()

        user.add_review(review)

        self.assertEqual(user.reviews, [review])

    def test_facade_enforces_unique_email_in_memory(self):
        facade = HBnBFacade()
        facade.create_user(
            {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
            }
        )

        with self.assertRaises(EmailAlreadyRegistered):
            facade.create_user(
                {
                    "first_name": "Grace",
                    "last_name": "Hopper",
                    "email": "ada@example.com",
                }
            )

    def test_facade_normalizes_email_before_uniqueness_check(self):
        facade = HBnBFacade()
        facade.create_user(
            {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
            }
        )

        with self.assertRaises(EmailAlreadyRegistered):
            facade.create_user(
                {
                    "first_name": "Grace",
                    "last_name": "Hopper",
                    "email": "  ADA@EXAMPLE.COM  ",
                }
            )

    def test_delete_user_soft_deletes_user(self):
        facade = HBnBFacade()
        user = facade.create_user(
            {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
            }
        )

        deleted_user = facade.delete_user(user.id)

        self.assertIs(deleted_user, user)
        self.assertFalse(user.is_active)
        self.assertNotIn(user, facade.get_all_users())
        with self.assertRaises(UserNotFound):
            facade.get_user(user.id)


if __name__ == "__main__":
    unittest.main()
