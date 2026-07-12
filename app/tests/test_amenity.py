import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.amenity import Amenity
from services.facade import HBnBFacade
from tests.orm_test_case import ORMTestCase
from utils.errors.amenity import AmenityNotFound
from utils.errors.user import AdminPrivilegesRequired


class TestAmenity(ORMTestCase):
    def test_create_valid_amenity(self):
        amenity = Amenity("Wi-Fi")

        self.assertEqual(amenity.name, "Wi-Fi")

    def test_amenity_trims_name(self):
        amenity = Amenity("  Wi-Fi  ")

        self.assertEqual(amenity.name, "Wi-Fi")

    def test_amenity_rejects_empty_name(self):
        for name in ("", "   "):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    Amenity(name)

    def test_amenity_rejects_non_string_name(self):
        for name in (None, 42, True):
            with self.subTest(name=name):
                with self.assertRaisesRegex(
                    ValueError,
                    "Amenity name must be a string",
                ):
                    Amenity(name)

    def test_amenity_rejects_name_longer_than_50_characters(self):
        with self.assertRaises(ValueError):
            Amenity("A" * 51)

    def test_amenity_accepts_name_at_50_character_boundary(self):
        amenity = Amenity("A" * 50)

        self.assertEqual(len(amenity.name), 50)

    def test_amenity_update_uses_validation(self):
        amenity = Amenity("Wi-Fi")

        with self.assertRaises(ValueError):
            amenity.update({"name": "   "})

    def test_to_dict(self):
        amenity = Amenity("Parking")

        self.assertEqual(
            amenity.to_dict(),
            {
                "id": amenity.id,
                "name": "Parking",
                "created_at": amenity.created_at.isoformat(),
                "updated_at": amenity.updated_at.isoformat(),
            },
        )

    def test_facade_raises_when_amenity_is_not_found(self):
        facade = HBnBFacade()

        with self.assertRaises(AmenityNotFound):
            facade.get_amenity("missing-id")

        with self.assertRaises(AmenityNotFound):
            facade.delete_amenity("missing-id")

    def test_facade_rejects_invalid_amenity_data(self):
        facade = HBnBFacade()

        with self.assertRaises(ValueError):
            facade.create_amenity({"name": "  "}, is_admin=True)

        amenity = facade.create_amenity(
            {"name": "Wi-Fi"},
            is_admin=True,
        )

        for invalid_data in ({}, {"name": None}, {"name": "  "}):
            with self.subTest(invalid_data=invalid_data):
                with self.assertRaises(ValueError):
                    facade.update_amenity(
                        amenity.id,
                        invalid_data,
                        is_admin=True,
                    )

    def test_update_raises_when_amenity_does_not_exist(self):
        facade = HBnBFacade()

        with self.assertRaises(AmenityNotFound):
            facade.update_amenity(
                "missing-id",
                {"name": "Pool"},
                is_admin=True,
            )

    def test_facade_creates_and_updates_amenity(self):
        facade = HBnBFacade()
        amenity = facade.create_amenity(
            {"name": "  Wi-Fi  "},
            is_admin=True,
        )

        self.assertEqual(amenity.name, "Wi-Fi")

        updated_amenity = facade.update_amenity(
            amenity.id,
            {"name": "Parking"},
            is_admin=True,
        )

        self.assertEqual(updated_amenity.name, "Parking")

    def test_facade_amenity_update_rejects_unsupported_fields(self):
        facade = HBnBFacade()
        amenity = facade.create_amenity(
            {"name": "Wi-Fi"},
            is_admin=True,
        )

        with self.assertRaisesRegex(
            ValueError,
            (
                "Invalid fields for amenity: is_active\\. "
                "Allowed fields: name"
            ),
        ):
            facade.update_amenity(
                amenity.id,
                {
                    "name": "Parking",
                    "is_active": False,
                },
                is_admin=True,
            )

        self.assertEqual(amenity.name, "Wi-Fi")

    def test_facade_amenity_mutations_require_admin(self):
        facade = HBnBFacade()

        with self.assertRaises(AdminPrivilegesRequired):
            facade.create_amenity({"name": "Wi-Fi"}, is_admin=False)

        amenity = facade.create_amenity(
            {"name": "Wi-Fi"},
            is_admin=True,
        )
        with self.assertRaises(AdminPrivilegesRequired):
            facade.update_amenity(
                amenity.id,
                {"name": "Parking"},
                is_admin=False,
            )


if __name__ == "__main__":
    unittest.main()
