import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.user import User
from services.facade import HBnBFacade
from utils.errors.user import (
    AdminPrivilegesRequired,
    EmailAlreadyInUse,
    EmailAlreadyRegistered,
    PasswordRequired,
    UserNotFound,
)


class TestUser(unittest.TestCase):
    def _create_facade_user(
        self,
        facade=None,
        email="ada@example.com",
        first_name="Ada",
        last_name="Lovelace",
    ):
        facade = facade or HBnBFacade()
        user = facade.create_user(
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": "test-password",
            },
            is_admin=True,
        )
        return facade, user

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

    def test_user_rejects_non_string_names_and_email(self):
        invalid_fields = (
            (None, "Lovelace", "ada@example.com", "First name"),
            ("Ada", 42, "ada@example.com", "Last name"),
            ("Ada", "Lovelace", False, "Email"),
        )

        for first_name, last_name, email, field_name in invalid_fields:
            with self.subTest(field_name=field_name):
                with self.assertRaisesRegex(
                    ValueError,
                    f"{field_name} must be a string",
                ):
                    User(first_name, last_name, email)

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

    def test_user_to_dict_serializes_complete_model(self):
        user = User(
            "Ada",
            "Lovelace",
            "ada@example.com",
            is_admin=True,
            is_active=False,
        )

        self.assertEqual(
            user.to_dict(),
            {
                "id": user.id,
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
                "is_admin": True,
                "is_active": False,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            },
        )

    def test_facade_user_update_rejects_unsupported_fields(self):
        facade = HBnBFacade()
        user = facade.create_user(
            {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
                "password": "test-password",
            },
            is_admin=True,
        )

        with self.assertRaisesRegex(
            ValueError,
            (
                "Invalid fields for user: is_admin\\. "
                "Allowed fields: first_name, last_name"
            ),
        ):
            facade.update_user(
                user.id,
                {"is_admin": True},
                current_user_id=user.id,
                is_admin=False,
            )

        self.assertFalse(user.is_admin)

    def test_facade_create_user_requires_password(self):
        facade = HBnBFacade()

        with self.assertRaisesRegex(
            PasswordRequired,
            "Password is required",
        ):
            facade.create_user(
                {
                    "first_name": "Ada",
                    "last_name": "Lovelace",
                    "email": "ada@example.com",
                },
                is_admin=True,
            )

        self.assertEqual(facade.get_all_users(), [])

    def test_facade_create_user_requires_admin(self):
        facade = HBnBFacade()

        with self.assertRaises(AdminPrivilegesRequired):
            facade.create_user(
                {
                    "first_name": "Ada",
                    "last_name": "Lovelace",
                    "email": "ada@example.com",
                    "password": "test-password",
                },
                is_admin=False,
            )

        self.assertEqual(facade.get_all_users(), [])

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
                "password": "test-password",
            },
            is_admin=True,
        )

        with self.assertRaises(EmailAlreadyRegistered):
            facade.create_user(
                {
                    "first_name": "Grace",
                    "last_name": "Hopper",
                    "email": "ada@example.com",
                    "password": "test-password",
                },
                is_admin=True,
            )

    def test_facade_normalizes_email_before_uniqueness_check(self):
        facade = HBnBFacade()
        facade.create_user(
            {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
                "password": "test-password",
            },
            is_admin=True,
        )

        with self.assertRaises(EmailAlreadyRegistered):
            facade.create_user(
                {
                    "first_name": "Grace",
                    "last_name": "Hopper",
                    "email": "  ADA@EXAMPLE.COM  ",
                    "password": "test-password",
                },
                is_admin=True,
            )

    def test_facade_updates_own_user_details(self):
        facade, user = self._create_facade_user()

        updated_user = facade.update_user(
            user.id,
            {
                "first_name": "Augusta",
                "last_name": "Byron",
            },
            current_user_id=user.id,
            is_admin=False,
        )

        self.assertIs(updated_user, user)
        self.assertEqual(user.first_name, "Augusta")
        self.assertEqual(user.last_name, "Byron")
        self.assertEqual(user.email, "ada@example.com")

    def test_facade_rejects_update_for_another_user(self):
        facade, user = self._create_facade_user()
        _, other_user = self._create_facade_user(
            facade=facade,
            email="grace@example.com",
            first_name="Grace",
            last_name="Hopper",
        )

        with self.assertRaises(AdminPrivilegesRequired):
            facade.update_user(
                user.id,
                {"first_name": "Augusta"},
                current_user_id=other_user.id,
                is_admin=False,
            )

        self.assertEqual(user.first_name, "Ada")

    def test_facade_rejects_email_update(self):
        facade, user = self._create_facade_user()

        with self.assertRaises(AdminPrivilegesRequired) as context:
            facade.update_user(
                user.id,
                {"email": "augusta@example.com"},
                current_user_id=user.id,
                is_admin=False,
            )

        self.assertEqual(
            str(context.exception),
            "Admin privileges required",
        )
        self.assertEqual(user.email, "ada@example.com")

    def test_facade_rejects_password_update(self):
        facade, user = self._create_facade_user()

        with self.assertRaises(AdminPrivilegesRequired) as context:
            facade.update_user(
                user.id,
                {"password": "new-password"},
                current_user_id=user.id,
                is_admin=False,
            )

        self.assertEqual(
            str(context.exception),
            "Admin privileges required",
        )
        self.assertTrue(user.verify_password("test-password"))

    def test_admin_updates_any_user_email_and_password(self):
        facade, user = self._create_facade_user()

        updated_user = facade.update_user(
            user.id,
            {
                "email": "  AUGUSTA@EXAMPLE.COM ",
                "password": "new-password",
            },
            current_user_id="admin-user",
            is_admin=True,
        )

        self.assertIs(updated_user, user)
        self.assertEqual(user.email, "augusta@example.com")
        self.assertTrue(user.verify_password("new-password"))
        self.assertFalse(user.verify_password("test-password"))

    def test_admin_user_update_rejects_duplicate_email(self):
        facade, user = self._create_facade_user()
        _, other_user = self._create_facade_user(
            facade=facade,
            email="grace@example.com",
            first_name="Grace",
            last_name="Hopper",
        )

        with self.assertRaises(EmailAlreadyInUse):
            facade.update_user(
                user.id,
                {"email": " GRACE@EXAMPLE.COM "},
                current_user_id=other_user.id,
                is_admin=True,
            )

        self.assertEqual(user.email, "ada@example.com")

    def test_facade_email_lookup_returns_none_when_missing(self):
        facade = HBnBFacade()

        self.assertIsNone(
            facade.get_user_by_email("missing@example.com")
        )

    def test_facade_user_update_raises_when_user_is_missing(self):
        facade = HBnBFacade()

        with self.assertRaises(UserNotFound):
            facade.update_user(
                "missing-user",
                {"first_name": "New"},
                current_user_id="missing-user",
                is_admin=False,
            )

    def test_soft_delete_user_sets_inactive_flag(self):
        facade = HBnBFacade()
        user = facade.create_user(
            {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
                "password": "test-password",
            },
            is_admin=True,
        )

        deleted_user = facade.soft_delete_user(user.id)

        self.assertIs(deleted_user, user)
        self.assertFalse(user.is_active)
        self.assertIn(user, facade.get_all_users())
        self.assertIs(facade.get_user(user.id), user)

    def test_delete_user_hard_deletes_user(self):
        facade = HBnBFacade()
        user = facade.create_user(
            {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
                "password": "test-password",
            },
            is_admin=True,
        )

        deleted_user = facade.delete_user(user.id)

        self.assertIs(deleted_user, user)
        self.assertIsNone(facade.user_repo.get(user.id))
        with self.assertRaises(UserNotFound):
            facade.get_user(user.id)


if __name__ == "__main__":
    unittest.main()
