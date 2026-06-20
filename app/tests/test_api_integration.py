import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from __init__ import create_app
    from services import facade
except ModuleNotFoundError as error:
    if error.name not in {"flask", "flask_restx"}:
        raise
    create_app = None
    facade = None


@unittest.skipIf(
    create_app is None,
    "Flask dependencies are not installed",
)
class TestApiErrorHandlerIntegration(unittest.TestCase):
    def setUp(self):
        for repository in (
            facade.user_repo,
            facade.place_repo,
            facade.review_repo,
            facade.amenity_repo,
        ):
            repository.clear()

        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_not_found_and_validation_errors_use_global_handlers(self):
        checks = (
            (
                self.client.get("/api/v1/users/missing"),
                404,
                {"error": "User 'missing' not found"},
            ),
            (
                self.client.get("/api/v1/places/missing"),
                404,
                {"error": "Place 'missing' not found"},
            ),
            (
                self.client.get("/api/v1/amenities/missing"),
                404,
                {"error": "Amenity 'missing' not found"},
            ),
            (
                self.client.get("/api/v1/reviews/missing"),
                404,
                {"error": "Review 'missing' not found"},
            ),
            (
                self.client.post(
                    "/api/v1/amenities/",
                    json={"name": "   "},
                ),
                400,
                {
                    "error": (
                        "Amenity name must be a non-empty string"
                    )
                },
            ),
        )

        for response, expected_status, expected_body in checks:
            self.assertEqual(response.status_code, expected_status)
            self.assertEqual(response.get_json(), expected_body)

    def test_conflict_and_business_rule_errors_use_global_handlers(self):
        user_data = {
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
        }
        user_response = self.client.post(
            "/api/v1/users/",
            json=user_data,
        )
        duplicate_response = self.client.post(
            "/api/v1/users/",
            json=user_data,
        )

        self.assertEqual(user_response.status_code, 201)
        self.assertEqual(duplicate_response.status_code, 409)
        self.assertEqual(
            duplicate_response.get_json(),
            {
                "error": (
                    "Email 'ada@example.com' is already registered"
                )
            },
        )

        owner_id = user_response.get_json()["id"]
        place_response = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Flat",
                "description": "Nice flat",
                "price": 100,
                "latitude": 0,
                "longitude": 0,
                "owner_id": owner_id,
            },
        )
        self.assertEqual(place_response.status_code, 201)

        review_response = self.client.post(
            (
                "/api/v1/places/"
                f"{place_response.get_json()['id']}/reviews"
            ),
            json={
                "text": "My own place",
                "rating": 5,
                "user_id": owner_id,
            },
        )

        self.assertEqual(review_response.status_code, 400)
        self.assertEqual(
            review_response.get_json(),
            {"error": "Owners cannot review their own place"},
        )

    def test_user_responses_exclude_internal_model_fields(self):
        created_response = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
            },
        )
        user_id = created_response.get_json()["id"]
        retrieved_response = self.client.get(
            f"/api/v1/users/{user_id}"
        )
        updated_response = self.client.put(
            f"/api/v1/users/{user_id}",
            json={"first_name": "Augusta Ada"},
        )
        listed_response = self.client.get("/api/v1/users/")

        expected_keys = {
            "id",
            "first_name",
            "last_name",
            "email",
        }

        for response in (
            created_response,
            retrieved_response,
            updated_response,
        ):
            self.assertEqual(
                set(response.get_json()),
                expected_keys,
            )

        self.assertEqual(
            set(listed_response.get_json()[0]),
            expected_keys,
        )

        user = facade.get_user(user_id)
        self.assertIn("is_admin", user.to_dict())
        self.assertIn("is_active", user.to_dict())
        self.assertIn("created_at", user.to_dict())
        self.assertIn("updated_at", user.to_dict())

    def test_user_soft_and_hard_delete_routes(self):
        soft_user_response = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Soft",
                "last_name": "Delete",
                "email": "soft@example.com",
            },
        )
        soft_user_id = soft_user_response.get_json()["id"]

        soft_delete_response = self.client.delete(
            f"/api/v1/users/{soft_user_id}/soft-delete"
        )

        self.assertEqual(soft_delete_response.status_code, 200)
        self.assertFalse(
            facade.user_repo.get(soft_user_id).is_active
        )

        hard_user_response = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Hard",
                "last_name": "Delete",
                "email": "hard@example.com",
            },
        )
        hard_user_id = hard_user_response.get_json()["id"]

        hard_delete_response = self.client.delete(
            f"/api/v1/users/{hard_user_id}"
        )

        self.assertEqual(hard_delete_response.status_code, 200)
        self.assertEqual(
            hard_delete_response.get_json(),
            {"message": "User permanently deleted"},
        )
        self.assertIsNone(facade.user_repo.get(hard_user_id))

    def test_review_update_rejects_user_and_place_changes(self):
        owner = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Owner",
                "last_name": "User",
                "email": "owner@example.com",
            },
        ).get_json()
        reviewer = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Review",
                "last_name": "Author",
                "email": "reviewer@example.com",
            },
        ).get_json()
        place = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Flat",
                "description": "Nice flat",
                "price": 100,
                "latitude": 0,
                "longitude": 0,
                "owner_id": owner["id"],
            },
        ).get_json()
        review = self.client.post(
            "/api/v1/reviews/",
            json={
                "text": "Great stay",
                "rating": 5,
                "user_id": reviewer["id"],
                "place_id": place["id"],
            },
        ).get_json()

        for payload in (
            {"user_id": owner["id"]},
            {"place_id": "another-place"},
        ):
            with self.subTest(payload=payload):
                response = self.client.put(
                    f"/api/v1/reviews/{review['id']}",
                    json=payload,
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(
                    response.get_json(),
                    {
                        "error": (
                            "Only review text and rating "
                            "can be updated"
                        )
                    },
                )

    def test_place_details_include_nested_relationships(self):
        owner = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Owner",
                "last_name": "User",
                "email": "owner@example.com",
            },
        ).get_json()
        reviewer = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Review",
                "last_name": "Author",
                "email": "reviewer@example.com",
            },
        ).get_json()
        amenity = self.client.post(
            "/api/v1/amenities/",
            json={"name": "Wi-Fi"},
        ).get_json()
        place = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Flat",
                "description": "Nice flat",
                "price": 100,
                "latitude": 0,
                "longitude": 0,
                "owner_id": owner["id"],
                "amenity_ids": [amenity["id"]],
            },
        ).get_json()
        review = self.client.post(
            "/api/v1/reviews/",
            json={
                "text": "Great stay",
                "rating": 5,
                "user_id": reviewer["id"],
                "place_id": place["id"],
            },
        ).get_json()

        response = self.client.get(
            f"/api/v1/places/{place['id']}"
        )
        place_data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            place_data["owner"],
            {
                "id": owner["id"],
                "first_name": "Owner",
                "last_name": "User",
                "email": "owner@example.com",
            },
        )
        self.assertEqual(
            place_data["amenities"],
            [{"id": amenity["id"], "name": "Wi-Fi"}],
        )
        self.assertEqual(
            place_data["reviews"],
            [
                {
                    "id": review["id"],
                    "text": "Great stay",
                    "rating": 5,
                    "user_id": reviewer["id"],
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
