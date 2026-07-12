import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.amenity import Amenity
from models.place import Place
from models.review import Review
from models.user import User
from services.facade import HBnBFacade
from tests.orm_test_case import ORMTestCase
from utils.errors.amenity import AmenityNotFound
from utils.errors.place import PlaceNotFound, UnauthorizedAction
from utils.errors.user import UserNotFound


class TestPlace(ORMTestCase):
    def setUp(self):
        super().setUp()
        self.owner = User("Ada", "Lovelace", "ada@example.com")

    def _create_facade_place(self, amenity_names=()):
        facade = HBnBFacade()
        owner = facade.create_user(
            {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
                "password": "test-password",
            },
            is_admin=True,
        )
        amenities = [
            facade.create_amenity({"name": name}, is_admin=True)
            for name in amenity_names
        ]
        place = facade.create_place(
            {
                "title": "Flat",
                "description": "Nice flat",
                "price": 100.0,
                "latitude": 0.0,
                "longitude": 0.0,
                "owner_id": owner.id,
                "amenity_ids": [
                    amenity.id for amenity in amenities
                ],
            }
        )
        return facade, owner, place, amenities

    def test_create_valid_place(self):
        place = Place(
            "Cozy flat",
            "Small but bright",
            120.5,
            -37.8136,
            144.9631,
            self.owner,
        )

        self.assertEqual(place.title, "Cozy flat")
        self.assertEqual(place.owner, self.owner)
        self.assertEqual(place.price, 120.5)
        self.assertTrue(place.is_active)
        self.assertEqual(place.reviews, [])
        self.assertEqual(place.amenities, [])

    def test_place_requires_user_owner(self):
        for invalid_owner in (None, "user-id", object()):
            with self.subTest(invalid_owner=invalid_owner):
                with self.assertRaisesRegex(
                    ValueError,
                    "Place owner must be a User",
                ):
                    Place(
                        "Cozy flat",
                        "Small but bright",
                        120.5,
                        -37.8136,
                        144.9631,
                        invalid_owner,
                    )

    def test_place_rejects_invalid_title(self):
        for title in ("", "   ", "P" * 101):
            with self.subTest(title=title):
                with self.assertRaises(ValueError):
                    Place(
                        title,
                        "Description",
                        100.0,
                        0.0,
                        0.0,
                        self.owner,
                    )

    def test_place_rejects_non_string_title(self):
        with self.assertRaisesRegex(
            ValueError,
            "Place title must be a string",
        ):
            Place(
                None,
                "Description",
                100.0,
                0.0,
                0.0,
                self.owner,
            )

    def test_place_trims_title(self):
        place = Place(
            "  Flat  ",
            "Description",
            100.0,
            0.0,
            0.0,
            self.owner,
        )

        self.assertEqual(place.title, "Flat")

    def test_place_accepts_title_at_100_character_boundary(self):
        place = Place(
            "P" * 100,
            "Description",
            100.0,
            0.0,
            0.0,
            self.owner,
        )

        self.assertEqual(len(place.title), 100)

    def test_place_rejects_non_positive_price(self):
        for price in (0, -1, True, "100"):
            with self.subTest(price=price):
                with self.assertRaises(ValueError):
                    Place(
                        "Flat",
                        "Description",
                        price,
                        0.0,
                        0.0,
                        self.owner,
                    )

    def test_place_validates_coordinate_ranges(self):
        invalid_coordinates = (
            (-90.1, 0.0),
            (90.1, 0.0),
            (0.0, -180.1),
            (0.0, 180.1),
        )

        for latitude, longitude in invalid_coordinates:
            with self.subTest(
                latitude=latitude,
                longitude=longitude,
            ):
                with self.assertRaises(ValueError):
                    Place(
                        "Flat",
                        "Description",
                        100.0,
                        latitude,
                        longitude,
                        self.owner,
                    )

    def test_place_rejects_non_numeric_coordinates(self):
        invalid_coordinates = (
            (True, 0.0),
            ("0", 0.0),
            (0.0, False),
            (0.0, "0"),
        )

        for latitude, longitude in invalid_coordinates:
            with self.subTest(
                latitude=latitude,
                longitude=longitude,
            ):
                with self.assertRaises(ValueError):
                    Place(
                        "Flat",
                        "Description",
                        100.0,
                        latitude,
                        longitude,
                        self.owner,
                    )

    def test_place_accepts_coordinate_boundaries(self):
        for latitude, longitude in (
            (-90, -180),
            (90, 180),
        ):
            with self.subTest(
                latitude=latitude,
                longitude=longitude,
            ):
                place = Place(
                    "Flat",
                    "Description",
                    100.0,
                    latitude,
                    longitude,
                    self.owner,
                )
                self.assertEqual(place.latitude, latitude)
                self.assertEqual(place.longitude, longitude)

    def test_place_update_uses_validation(self):
        place = Place(
            "Flat",
            "Description",
            100.0,
            0.0,
            0.0,
            self.owner,
        )

        with self.assertRaises(ValueError):
            place.update({"price": -10})

    def test_add_review(self):
        place = Place("Flat", "Nice flat", 100.0, 0.0, 0.0, self.owner)
        reviewer = User("Grace", "Hopper", "grace@example.com")
        review = Review("Great", 5, place, reviewer)

        place.add_review(review)

        self.assertEqual(place.reviews, [review])

    def test_add_amenity(self):
        amenity = Amenity("Parking")
        place = Place("Flat", "Nice flat", 100.0, 0.0, 0.0, self.owner)

        place.add_amenity(amenity)

        self.assertEqual(place.amenities, [amenity])

    def test_place_to_dict_serializes_complete_model(self):
        amenity = Amenity("Parking")
        place = Place(
            "Flat",
            "Nice flat",
            100.0,
            -37.8,
            144.9,
            self.owner,
            is_active=False,
        )
        place.add_amenity(amenity)

        self.assertEqual(
            place.to_dict(),
            {
                "id": place.id,
                "title": "Flat",
                "description": "Nice flat",
                "price": 100.0,
                "latitude": -37.8,
                "longitude": 144.9,
                "owner_id": self.owner.id,
                "is_active": False,
                "amenities": [amenity.id],
                "created_at": place.created_at.isoformat(),
                "updated_at": place.updated_at.isoformat(),
            },
        )

    def test_facade_validates_owner_exists_in_database(self):
        facade = HBnBFacade()

        with self.assertRaises(UserNotFound):
            facade.create_place(
                {
                    "title": "Flat",
                    "description": "Nice flat",
                    "price": 100.0,
                    "latitude": 0.0,
                    "longitude": 0.0,
                    "owner_id": self.owner.id,
                }
            )

    def test_facade_place_update_rejects_unsupported_fields(self):
        facade, owner, place, _ = self._create_facade_place()
        replacement_owner = facade.create_user(
            {
                "first_name": "Grace",
                "last_name": "Hopper",
                "email": "grace@example.com",
                "password": "test-password",
            },
            is_admin=True,
        )

        with self.assertRaisesRegex(
            ValueError,
            (
                "Invalid fields for place: owner_id\\. Allowed fields: "
                "amenity_ids, description, latitude, longitude, price, title"
            ),
        ):
            facade.update_place(
                place.id,
                {"owner_id": replacement_owner.id},
                current_user_id=owner.id,
                is_admin=False,
            )

        self.assertIs(place.owner, owner)
        self.assertIn(place, owner.places)
        self.assertNotIn(place, replacement_owner.places)

    def test_facade_updates_place_fields(self):
        facade, owner, place, _ = self._create_facade_place()

        updated_place = facade.update_place(
            place.id,
            {
                "title": "Beach house",
                "description": "Ocean views",
                "price": 250.0,
                "latitude": -37.8,
                "longitude": 144.9,
            },
            current_user_id=owner.id,
            is_admin=False,
        )

        self.assertIs(updated_place, place)
        self.assertEqual(place.title, "Beach house")
        self.assertEqual(place.description, "Ocean views")
        self.assertEqual(place.price, 250.0)
        self.assertEqual(place.latitude, -37.8)
        self.assertEqual(place.longitude, 144.9)

    def test_facade_rejects_place_update_by_non_owner(self):
        facade, _, place, _ = self._create_facade_place()
        other_user = facade.create_user(
            {
                "first_name": "Grace",
                "last_name": "Hopper",
                "email": "grace@example.com",
                "password": "test-password",
            },
            is_admin=True,
        )

        with self.assertRaises(UnauthorizedAction):
            facade.update_place(
                place.id,
                {"title": "Beach house"},
                current_user_id=other_user.id,
                is_admin=False,
            )

        self.assertEqual(place.title, "Flat")

    def test_admin_can_update_place_owned_by_another_user(self):
        facade, _, place, _ = self._create_facade_place()

        updated_place = facade.update_place(
            place.id,
            {"title": "Admin updated"},
            current_user_id="admin-user",
            is_admin=True,
        )

        self.assertIs(updated_place, place)
        self.assertEqual(place.title, "Admin updated")

    def test_facade_rejects_place_update_without_authenticated_user(self):
        facade, _, place, _ = self._create_facade_place()

        with self.assertRaises(UnauthorizedAction):
            facade.update_place(
                place.id,
                {"title": "Beach house"},
                current_user_id=None,
                is_admin=False,
            )

        self.assertEqual(place.title, "Flat")

    def test_facade_replaces_and_clears_place_amenities(self):
        facade, owner, place, original = self._create_facade_place(
            ("Wi-Fi",)
        )
        pool = facade.create_amenity({"name": "Pool"}, is_admin=True)
        parking = facade.create_amenity(
            {"name": "Parking"},
            is_admin=True,
        )

        facade.update_place(
            place.id,
            {"amenity_ids": [pool.id, parking.id]},
            current_user_id=owner.id,
            is_admin=False,
        )

        self.assertCountEqual(place.amenities, [pool, parking])
        self.assertNotIn(original[0], place.amenities)

        facade.update_place(
            place.id,
            {"amenity_ids": []},
            current_user_id=owner.id,
            is_admin=False,
        )

        self.assertEqual(place.amenities, [])

    def test_facade_rejects_unknown_amenity_without_changing_place(self):
        facade, owner, place, amenities = self._create_facade_place(
            ("Wi-Fi",)
        )

        with self.assertRaises(AmenityNotFound):
            facade.update_place(
                place.id,
                {"amenity_ids": ["missing-amenity"]},
                current_user_id=owner.id,
                is_admin=False,
            )

        self.assertEqual(place.amenities, amenities)

    def test_facade_place_update_raises_when_place_is_missing(self):
        facade = HBnBFacade()

        with self.assertRaises(PlaceNotFound):
            facade.update_place(
                "missing-place",
                {"title": "Beach house"},
                current_user_id="missing-owner",
                is_admin=False,
            )

    def test_delete_place_hard_deletes_place(self):
        facade, _, place, _ = self._create_facade_place()

        deleted_place = facade.delete_place(place.id)

        self.assertIs(deleted_place, place)
        self.assertIsNone(facade.place_repo.get(place.id))
        self.assertNotIn(place, facade.get_all_places())
        with self.assertRaises(PlaceNotFound):
            facade.get_place(place.id)
        with self.assertRaises(PlaceNotFound):
            facade.delete_place(place.id)


if __name__ == "__main__":
    unittest.main()
