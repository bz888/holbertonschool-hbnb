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


if __name__ == "__main__":
    unittest.main()
