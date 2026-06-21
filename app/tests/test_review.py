import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.place import Place
from models.review import Review
from models.user import User
from services.facade import HBnBFacade
from utils.errors.place import PlaceNotFound
from utils.errors.review import OwnerCannotReviewOwnPlace, ReviewNotFound
from utils.errors.user import UserNotFound


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

    def test_review_requires_place_and_user_instances(self):
        for invalid_place in (None, "place-id", object()):
            with self.subTest(invalid_place=invalid_place):
                with self.assertRaisesRegex(
                    ValueError,
                    "Review place must be a Place",
                ):
                    Review(
                        "Great stay",
                        5,
                        invalid_place,
                        self.user,
                    )

        for invalid_user in (None, "user-id", object()):
            with self.subTest(invalid_user=invalid_user):
                with self.assertRaisesRegex(
                    ValueError,
                    "Review user must be a User",
                ):
                    Review(
                        "Great stay",
                        5,
                        self.place,
                        invalid_user,
                    )

    def test_review_rejects_empty_text(self):
        for text in ("", "   "):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    Review(
                        text,
                        5,
                        self.place,
                        self.user,
                    )

    def test_review_rejects_non_string_text(self):
        with self.assertRaisesRegex(
            ValueError,
            "Review text must be a string",
        ):
            Review(None, 5, self.place, self.user)

    def test_review_trims_text(self):
        review = Review(
            "  Great stay  ",
            5,
            self.place,
            self.user,
        )

        self.assertEqual(review.text, "Great stay")

    def test_review_rejects_rating_outside_1_to_5(self):
        for rating in (0, 6, -1, 1.5, True, "5"):
            with self.subTest(rating=rating):
                with self.assertRaises(ValueError):
                    Review(
                        "Great stay",
                        rating,
                        self.place,
                        self.user,
                    )

    def test_review_accepts_rating_boundaries(self):
        for rating in (1, 5):
            with self.subTest(rating=rating):
                review = Review(
                    "Great stay",
                    rating,
                    self.place,
                    self.user,
                )
                self.assertEqual(review.rating, rating)

    def test_review_update_uses_validation(self):
        review = Review(
            "Great stay",
            5,
            self.place,
            self.user,
        )

        with self.assertRaises(ValueError):
            review.update({"rating": 6})

    def test_review_to_dict_serializes_complete_model(self):
        review = Review(
            "Great stay",
            5,
            self.place,
            self.user,
        )

        self.assertEqual(
            review.to_dict(),
            {
                "id": review.id,
                "text": "Great stay",
                "rating": 5,
                "place_id": self.place.id,
                "user_id": self.user.id,
                "created_at": review.created_at.isoformat(),
                "updated_at": review.updated_at.isoformat(),
            },
        )

    def test_facade_review_update_only_changes_text_and_rating(self):
        facade, _, reviewer, place, review = self._create_review(
            facade=HBnBFacade()
        )

        updated_review = facade.update_review(
            review.id,
            {
                "text": "Updated review",
                "rating": 4,
            },
        )

        self.assertEqual(updated_review.text, "Updated review")
        self.assertEqual(updated_review.rating, 4)
        self.assertIs(updated_review.user, reviewer)
        self.assertIs(updated_review.place, place)

    def test_facade_review_update_rejects_unsupported_fields(self):
        facade, _, reviewer, place, review = self._create_review(
            facade=HBnBFacade()
        )

        for field, value in (
            ("user_id", "another-user"),
            ("place_id", "another-place"),
            ("is_active", False),
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    ValueError,
                    (
                        f"Invalid fields for review: {field}\\. "
                        "Allowed fields: rating, text"
                    ),
                ):
                    facade.update_review(
                        review.id,
                        {field: value},
                    )

        self.assertIs(review.user, reviewer)
        self.assertIs(review.place, place)

    def test_facade_validates_review_relationships_in_memory(self):
        facade = HBnBFacade()

        with self.assertRaises(PlaceNotFound):
            facade.create_review(
                {
                    "text": "Great stay",
                    "rating": 5,
                    "place_id": self.place.id,
                    "user_id": self.user.id,
                }
            )

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

        with self.assertRaises(UserNotFound):
            facade.create_review(
                {
                    "text": "Great stay",
                    "rating": 5,
                    "place_id": place.id,
                    "user_id": self.user.id,
                }
            )

    def test_facade_links_review_to_place_and_user(self):
        facade = HBnBFacade()
        owner = facade.create_user(
            {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
            }
        )
        reviewer = facade.create_user(
            {
                "first_name": "Grace",
                "last_name": "Hopper",
                "email": "grace@example.com",
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

        review = facade.create_review(
            {
                "text": "Great stay",
                "rating": 5,
                "place_id": place.id,
                "user_id": reviewer.id,
            }
        )

        self.assertIn(review, place.reviews)
        self.assertIn(review, reviewer.reviews)

    def test_owner_cannot_review_own_place(self):
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

        with self.assertRaises(OwnerCannotReviewOwnPlace):
            facade.create_review(
                {
                    "text": "Great stay",
                    "rating": 5,
                    "place_id": place.id,
                    "user_id": owner.id,
                }
            )

    def test_reviews_can_be_listed_by_user(self):
        facade, _, reviewer, _, review = self._create_review(facade=HBnBFacade())

        self.assertEqual(
            facade.get_reviews_by_user(reviewer.id),
            [review],
        )

    def test_deleting_reviewer_preserves_review(self):
        facade, _, reviewer, place, review = self._create_review(
            facade=HBnBFacade()
        )

        facade.soft_delete_user(reviewer.id)

        self.assertFalse(reviewer.is_active)
        self.assertTrue(place.is_active)
        self.assertIs(facade.get_review(review.id), review)
        self.assertIn(review, facade.get_all_reviews())
        self.assertIn(review, place.reviews)
        self.assertEqual(review.to_dict()["user_id"], reviewer.id)
        self.assertEqual(
            facade.get_reviews_by_user(reviewer.id),
            [review],
        )

    def test_deleting_place_preserves_review(self):
        facade, _, _, place, review = self._create_review(
            facade=HBnBFacade()
        )

        facade.delete_place(place.id)

        self.assertIsNone(facade.place_repo.get(place.id))
        self.assertIs(facade.get_review(review.id), review)
        self.assertIn(review, facade.get_all_reviews())
        self.assertEqual(review.to_dict()["place_id"], place.id)
        with self.assertRaises(PlaceNotFound):
            facade.get_reviews_by_place(place.id)

    def test_deleting_owner_deactivates_owned_places(self):
        facade, owner, _, place, review = self._create_review(
            facade=HBnBFacade()
        )

        facade.soft_delete_user(owner.id)

        self.assertFalse(owner.is_active)
        self.assertFalse(place.is_active)
        self.assertIs(facade.get_review(review.id), review)

    def test_deleting_review_unlinks_relationships(self):
        facade, _, reviewer, place, review = self._create_review(
            facade=HBnBFacade()
        )

        facade.delete_review(review.id)

        self.assertNotIn(review, reviewer.reviews)
        self.assertNotIn(review, place.reviews)
        with self.assertRaises(ReviewNotFound):
            facade.get_review(review.id)

    def _create_review(self, facade):
        owner = facade.create_user(
            {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
            }
        )
        reviewer = facade.create_user(
            {
                "first_name": "Grace",
                "last_name": "Hopper",
                "email": "grace@example.com",
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
        review = facade.create_review(
            {
                "text": "Great stay",
                "rating": 5,
                "place_id": place.id,
                "user_id": reviewer.id,
            }
        )
        return facade, owner, reviewer, place, review


if __name__ == "__main__":
    unittest.main()
