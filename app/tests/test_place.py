import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.amenity import Amenity
from models.place import Place
from models.user import User
from services.facade import HBnBFacade
from utils.errors.place import PlaceNotFound
from utils.errors.user import UserNotFound


class TestPlace(unittest.TestCase):
    def setUp(self):
        self.owner = User("Ada", "Lovelace", "ada@example.com")

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

    def test_add_review(self):
        place = Place("Flat", "Nice flat", 100.0, 0.0, 0.0, self.owner)
        review = object()

        place.add_review(review)

        self.assertEqual(place.reviews, [review])

    def test_add_amenity(self):
        amenity = Amenity("Parking")
        place = Place("Flat", "Nice flat", 100.0, 0.0, 0.0, self.owner)

        place.add_amenity(amenity)

        self.assertEqual(place.amenities, [amenity])

    def test_facade_validates_owner_exists_in_memory(self):
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

    def test_delete_place_soft_deletes_place(self):
        facade = HBnBFacade()
        owner = facade.create_user(
            {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
            }
        )
        place = facade.create_place(
            {
                "title": "Flat",
                "description": "Nice flat",
                "price": 100.0,
                "latitude": 0.0,
                "longitude": 0.0,
                "owner_id": owner.id,
            }
        )

        deleted_place = facade.delete_place(place.id)

        self.assertIs(deleted_place, place)
        self.assertFalse(place.is_active)
        self.assertNotIn(place, facade.get_all_places())
        with self.assertRaises(PlaceNotFound):
            facade.get_place(place.id)


if __name__ == "__main__":
    unittest.main()
