import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.place import Place
from models.review import Review
from models.user import User
from services.facade import HBnBFacade


class TestReview(unittest.TestCase):
    def setUp(self):
        self.user = User("Ada", "Lovelace", "ada@example.com")
        self.place = Place("Flat", "Nice flat", 100.0, 0.0, 0.0, self.user)

    def test_create_valid_review(self):
        review = Review("Great stay", 5, self.place, self.user)

        self.assertEqual(review.text, "Great stay")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.place, self.place)
        self.assertEqual(review.user, self.user)

    def test_facade_validates_review_relationships_in_memory(self):
        facade = HBnBFacade()

        with self.assertRaises(ValueError):
            facade.create_review(
                {
                    "text": "Great stay",
                    "rating": 5,
                    "place_id": self.place.id,
                    "user_id": self.user.id,
                }
            )

    def test_facade_links_review_to_place_and_user(self):
        facade = HBnBFacade()
        user = facade.create_user(
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
                "owner_id": user.id,
            }
        )

        review = facade.create_review(
            {
                "text": "Great stay",
                "rating": 5,
                "place_id": place.id,
                "user_id": user.id,
            }
        )

        self.assertIn(review, place.reviews)
        self.assertIn(review, user.reviews)


if __name__ == "__main__":
    unittest.main()
