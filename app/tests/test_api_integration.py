import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from flask_jwt_extended import create_access_token

    from __init__ import create_app
    from services import facade
except ModuleNotFoundError as error:
    if error.name not in {
        "flask",
        "flask_jwt_extended",
        "flask_restx",
    }:
        raise
    create_app = None
    create_access_token = None
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
        self.app.config["JWT_SECRET_KEY"] = (
            "test-secret-key-with-at-least-32-characters"
        )
        self.client = self.app.test_client()

    def _auth_headers(self, user_id, is_admin=False):
        with self.app.app_context():
            token = create_access_token(
                identity=user_id,
                additional_claims={"is_admin": is_admin},
            )

        return {"Authorization": f"Bearer {token}"}

    def _create_user(
        self,
        first_name="Owner",
        last_name="User",
        email="owner@example.com",
    ):
        response = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": "test-password",
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def _create_amenity(self, name="Wi-Fi"):
        response = self.client.post(
            "/api/v1/amenities/",
            json={"name": name},
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def _create_place(self, owner_id, amenity_ids=None):
        place_data = {
            "title": "Flat",
            "description": "Nice flat",
            "price": 100,
            "latitude": 0,
            "longitude": 0,
        }
        if amenity_ids is not None:
            place_data["amenity_ids"] = amenity_ids

        response = self.client.post(
            "/api/v1/places/",
            json=place_data,
            headers=self._auth_headers(owner_id),
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def _create_review(self, place_id, user_id):
        response = self.client.post(
            "/api/v1/reviews/",
            json={
                "text": "Great stay",
                "rating": 5,
                "place_id": place_id,
            },
            headers=self._auth_headers(user_id),
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def test_not_found_and_validation_errors_use_global_handlers(self):
        amenity = self.client.post(
            "/api/v1/amenities/",
            json={"name": "Wi-Fi"},
        ).get_json()

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
            (
                self.client.put(
                    f"/api/v1/amenities/{amenity['id']}",
                    json={},
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

    def test_missing_mutation_and_nested_routes_return_404(self):
        reviewer = self._create_user(
            first_name="Review",
            last_name="Author",
            email="reviewer@example.com",
        )
        checks = (
            (
                self.client.put(
                    "/api/v1/users/missing",
                    json={"email": "new@example.com"},
                    headers=self._auth_headers(reviewer["id"]),
                ),
                {"error": "User 'missing' not found"},
            ),
            (
                self.client.delete("/api/v1/users/missing"),
                {"error": "User 'missing' not found"},
            ),
            (
                self.client.get("/api/v1/users/missing/reviews"),
                {"error": "User 'missing' not found"},
            ),
            (
                self.client.put(
                    "/api/v1/amenities/missing",
                    json={"name": "Pool"},
                ),
                {"error": "Amenity 'missing' not found"},
            ),
            (
                self.client.delete("/api/v1/amenities/missing"),
                {"error": "Amenity 'missing' not found"},
            ),
            (
                self.client.put(
                    "/api/v1/places/missing",
                    json={"title": "Beach house"},
                    headers=self._auth_headers(reviewer["id"]),
                ),
                {"error": "Place 'missing' not found"},
            ),
            (
                self.client.delete("/api/v1/places/missing"),
                {"error": "Place 'missing' not found"},
            ),
            (
                self.client.get("/api/v1/places/missing/reviews"),
                {"error": "Place 'missing' not found"},
            ),
            (
                self.client.post(
                    "/api/v1/places/missing/reviews",
                    json={
                        "text": "Great stay",
                        "rating": 5,
                    },
                    headers=self._auth_headers(reviewer["id"]),
                ),
                {"error": "Place 'missing' not found"},
            ),
            (
                self.client.put(
                    "/api/v1/reviews/missing",
                    json={"rating": 4},
                    headers=self._auth_headers(reviewer["id"]),
                ),
                {"error": "Review 'missing' not found"},
            ),
            (
                self.client.delete(
                    "/api/v1/reviews/missing",
                    headers=self._auth_headers(reviewer["id"]),
                ),
                {"error": "Review 'missing' not found"},
            ),
        )

        for response, expected_body in checks:
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.get_json(), expected_body)

    def test_conflict_and_business_rule_errors_use_global_handlers(self):
        user_data = {
            "first_name": "Ada",
            "last_name": "Lovelace",
            "email": "ada@example.com",
            "password": "test-password",
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
        self.assertEqual(duplicate_response.status_code, 400)
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
            },
            headers=self._auth_headers(owner_id),
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
            },
            headers=self._auth_headers(owner_id),
        )

        self.assertEqual(review_response.status_code, 400)
        self.assertEqual(
            review_response.get_json(),
            {"error": "Owners cannot review their own place"},
        )

    def test_jwt_protected_write_routes_require_token(self):
        owner = self._create_user()
        reviewer = self._create_user(
            first_name="Review",
            last_name="Author",
            email="reviewer@example.com",
        )
        place = self._create_place(owner["id"])
        review = self._create_review(place["id"], reviewer["id"])

        checks = (
            self.client.post(
                "/api/v1/places/",
                json={
                    "title": "New flat",
                    "price": 100,
                    "latitude": 0,
                    "longitude": 0,
                },
            ),
            self.client.put(
                f"/api/v1/places/{place['id']}",
                json={"title": "Updated flat"},
            ),
            self.client.post(
                "/api/v1/reviews/",
                json={
                    "text": "Great stay",
                    "rating": 5,
                    "place_id": place["id"],
                },
            ),
            self.client.post(
                f"/api/v1/places/{place['id']}/reviews",
                json={
                    "text": "Great stay",
                    "rating": 5,
                },
            ),
            self.client.put(
                f"/api/v1/reviews/{review['id']}",
                json={"rating": 4},
            ),
            self.client.delete(f"/api/v1/reviews/{review['id']}"),
            self.client.put(
                f"/api/v1/users/{owner['id']}",
                json={"first_name": "Updated"},
            ),
        )

        for response in checks:
            self.assertEqual(response.status_code, 401)
            self.assertEqual(
                response.get_json(),
                {"msg": "Missing Authorization Header"},
            )

    def test_place_get_routes_remain_public(self):
        owner = self._create_user()
        place = self._create_place(owner["id"])

        list_response = self.client.get("/api/v1/places/")
        detail_response = self.client.get(
            f"/api/v1/places/{place['id']}"
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(list_response.get_json()[0]["id"], place["id"])
        self.assertEqual(detail_response.get_json()["id"], place["id"])

    def test_create_routes_use_jwt_identity_for_relationships(self):
        owner = self._create_user()
        reviewer = self._create_user(
            first_name="Review",
            last_name="Author",
            email="reviewer@example.com",
        )
        spoofed_user = self._create_user(
            first_name="Spoofed",
            last_name="User",
            email="spoofed@example.com",
        )

        place_response = self.client.post(
            "/api/v1/places/",
            json={
                "title": "Flat",
                "description": "Nice flat",
                "price": 100,
                "latitude": 0,
                "longitude": 0,
                "owner_id": spoofed_user["id"],
            },
            headers=self._auth_headers(owner["id"]),
        )
        place = place_response.get_json()

        review_response = self.client.post(
            "/api/v1/reviews/",
            json={
                "text": "Great stay",
                "rating": 5,
                "place_id": place["id"],
                "user_id": spoofed_user["id"],
            },
            headers=self._auth_headers(reviewer["id"]),
        )

        self.assertEqual(place_response.status_code, 201)
        self.assertEqual(place["owner_id"], owner["id"])
        self.assertEqual(review_response.status_code, 201)
        self.assertEqual(
            review_response.get_json()["user_id"],
            reviewer["id"],
        )

    def test_user_responses_exclude_internal_model_fields(self):
        created_response = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
                "password": "correct horse battery staple",
            },
        )
        user_id = created_response.get_json()["id"]
        retrieved_response = self.client.get(
            f"/api/v1/users/{user_id}"
        )
        updated_response = self.client.put(
            f"/api/v1/users/{user_id}",
            json={"first_name": "Augusta Ada"},
            headers=self._auth_headers(user_id),
        )
        listed_response = self.client.get("/api/v1/users/")

        expected_keys = {
            "id",
            "first_name",
            "last_name",
            "email",
        }

        self.assertEqual(created_response.status_code, 201)
        self.assertEqual(
            set(created_response.get_json()),
            {"id", "message"},
        )
        self.assertEqual(
            created_response.get_json()["message"],
            "User successfully created",
        )

        for response in (retrieved_response, updated_response):
            self.assertEqual(
                set(response.get_json()),
                expected_keys,
            )

        self.assertEqual(updated_response.status_code, 200)
        self.assertEqual(
            updated_response.get_json()["first_name"],
            "Augusta Ada",
        )

        self.assertEqual(
            set(listed_response.get_json()[0]),
            expected_keys,
        )

        user = facade.get_user(user_id)
        self.assertNotEqual(
            user.password,
            "correct horse battery staple",
        )
        with self.app.app_context():
            self.assertTrue(
                user.verify_password(
                    "correct horse battery staple",
                )
            )
        self.assertIn("is_admin", user.to_dict())
        self.assertIn("is_active", user.to_dict())
        self.assertIn("created_at", user.to_dict())
        self.assertIn("updated_at", user.to_dict())

    def test_user_registration_hashes_password_and_hides_it(self):
        plain_password = "correct horse battery staple"
        created_response = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Password",
                "last_name": "Check",
                "email": "password-check@example.com",
                "password": plain_password,
            },
        )
        created_body = created_response.get_json()

        self.assertEqual(created_response.status_code, 201)
        self.assertEqual(
            set(created_body),
            {"id", "message"},
        )
        self.assertNotIn("password", created_body)

        user = facade.get_user(created_body["id"])
        self.assertNotEqual(user.password, plain_password)
        with self.app.app_context():
            self.assertTrue(user.verify_password(plain_password))

        retrieved_response = self.client.get(
            f"/api/v1/users/{created_body['id']}"
        )
        retrieved_body = retrieved_response.get_json()

        self.assertEqual(retrieved_response.status_code, 200)
        self.assertNotIn("password", retrieved_body)
        self.assertEqual(
            set(retrieved_body),
            {"id", "first_name", "last_name", "email"},
        )

    def test_amenity_and_review_responses_exclude_timestamps(self):
        owner = self._create_user()
        reviewer = self._create_user(
            first_name="Review",
            last_name="Author",
            email="reviewer@example.com",
        )
        amenity = self._create_amenity()
        place = self._create_place(
            owner["id"],
            amenity_ids=[amenity["id"]],
        )
        review = self._create_review(place["id"], reviewer["id"])

        amenity_keys = {"id", "name"}
        review_keys = {
            "id",
            "text",
            "rating",
            "place_id",
            "user_id",
        }

        amenity_responses = (
            amenity,
            self.client.get(
                f"/api/v1/amenities/{amenity['id']}"
            ).get_json(),
            self.client.get("/api/v1/amenities/").get_json()[0],
        )
        amenity_update_response = self.client.put(
            f"/api/v1/amenities/{amenity['id']}",
            json={"name": "Parking"},
        )
        review_update_response = self.client.put(
            f"/api/v1/reviews/{review['id']}",
            json={"rating": 4},
            headers=self._auth_headers(reviewer["id"]),
        )
        review_responses = (
            review,
            self.client.get(
                f"/api/v1/reviews/{review['id']}"
            ).get_json(),
            self.client.get("/api/v1/reviews/").get_json()[0],
            self.client.get(
                f"/api/v1/users/{reviewer['id']}/reviews"
            ).get_json()[0],
        )

        for response in amenity_responses:
            self.assertEqual(set(response), amenity_keys)

        self.assertEqual(amenity_update_response.status_code, 200)
        self.assertEqual(
            amenity_update_response.get_json(),
            {"message": "Amenity updated successfully"},
        )

        self.assertEqual(review_update_response.status_code, 200)
        self.assertEqual(
            review_update_response.get_json(),
            {"message": "Review updated successfully"},
        )

        for response in review_responses:
            self.assertEqual(set(response), review_keys)

        self.assertEqual(
            facade.get_review(review["id"]).rating,
            4,
        )

        place_update_response = self.client.put(
            f"/api/v1/places/{place['id']}",
            json={"title": "Updated Flat"},
            headers=self._auth_headers(owner["id"]),
        )
        self.assertEqual(place_update_response.status_code, 200)
        self.assertEqual(
            place_update_response.get_json(),
            {"message": "Place updated successfully"},
        )
        self.assertEqual(
            facade.get_place(place["id"]).title,
            "Updated Flat",
        )

        place_review = self.client.get(
            f"/api/v1/places/{place['id']}/reviews"
        ).get_json()[0]
        self.assertEqual(
            set(place_review),
            {"id", "text", "rating", "place_id", "user_id"},
        )

    def test_hard_delete_routes(self):
        # soft_user_response = self.client.post(
        #     "/api/v1/users/",
        #     json={
        #         "first_name": "Soft",
        #         "last_name": "Delete",
        #         "email": "soft@example.com",
        #     },
        # )
        # soft_user_id = soft_user_response.get_json()["id"]

        # soft_delete_response = self.client.delete(
        #     f"/api/v1/users/{soft_user_id}/soft-delete"
        # )

        # self.assertEqual(soft_delete_response.status_code, 200)
        # self.assertFalse(
        #     facade.user_repo.get(soft_user_id).is_active
        # )

        hard_user_response = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Hard",
                "last_name": "Delete",
                "email": "hard@example.com",
                "password": "test-password",
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
        owner = self._create_user()
        reviewer = self._create_user(
            first_name="Review",
            last_name="Author",
            email="reviewer@example.com",
        )
        place = self._create_place(owner["id"])
        review = self._create_review(place["id"], reviewer["id"])

        for payload in (
            {"user_id": owner["id"]},
            {"place_id": "another-place"},
        ):
            with self.subTest(payload=payload):
                response = self.client.put(
                    f"/api/v1/reviews/{review['id']}",
                    json=payload,
                    headers=self._auth_headers(reviewer["id"]),
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(
                    response.get_json(),
                    {
                        "error": (
                            "Invalid fields for review: "
                            f"{next(iter(payload))}. "
                            "Allowed fields: rating, text"
                        )
                    },
                )

    def test_updates_reject_unsupported_fields(self):
        owner = self._create_user()
        replacement_owner = self._create_user(
            first_name="Replacement",
            last_name="Owner",
            email="replacement@example.com",
        )
        amenity = self._create_amenity()
        place = self._create_place(owner["id"])

        checks = (
            (
                self.client.put(
                    f"/api/v1/users/{owner['id']}",
                    json={"is_admin": True},
                    headers=self._auth_headers(owner["id"]),
                ),
                {
                    "error": (
                        "Invalid fields for user: is_admin. "
                        "Allowed fields: email, first_name, last_name"
                    )
                },
            ),
            (
                self.client.put(
                    f"/api/v1/amenities/{amenity['id']}",
                    json={
                        "name": "Parking",
                        "is_active": False,
                    },
                ),
                {
                    "error": (
                        "Invalid fields for amenity: is_active. "
                        "Allowed fields: name"
                    )
                },
            ),
            (
                self.client.put(
                    f"/api/v1/places/{place['id']}",
                    json={"owner_id": replacement_owner["id"]},
                    headers=self._auth_headers(owner["id"]),
                ),
                {
                    "error": (
                        "Invalid fields for place: owner_id. "
                        "Allowed fields: amenity_ids, description, "
                        "latitude, longitude, price, title"
                    )
                },
            ),
        )

        for response, expected_body in checks:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.get_json(), expected_body)

        self.assertFalse(facade.get_user(owner["id"]).is_admin)
        self.assertEqual(
            facade.get_amenity(amenity["id"]).name,
            "Wi-Fi",
        )
        self.assertEqual(
            facade.get_place(place["id"]).owner.id,
            owner["id"],
        )

    def test_place_delete_route_hard_deletes_place(self):
        owner = self._create_user()
        place = self._create_place(owner["id"])

        response = self.client.delete(
            f"/api/v1/places/{place['id']}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {"message": "Place deleted successfully"},
        )
        self.assertIsNone(facade.place_repo.get(place["id"]))

        missing_response = self.client.get(
            f"/api/v1/places/{place['id']}"
        )
        self.assertEqual(missing_response.status_code, 404)
        self.assertEqual(
            missing_response.get_json(),
            {"error": f"Place '{place['id']}' not found"},
        )

    def test_place_update_route_succeeds(self):
        owner = self._create_user()
        place = self._create_place(owner["id"])

        response = self.client.put(
            f"/api/v1/places/{place['id']}",
            json={"title": "Beach house"},
            headers=self._auth_headers(owner["id"]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {"message": "Place updated successfully"},
        )
        self.assertEqual(
            facade.get_place(place["id"]).title,
            "Beach house",
        )

    def test_place_update_by_non_owner_returns_forbidden(self):
        owner = self._create_user()
        other_user = self._create_user(
            first_name="Other",
            last_name="User",
            email="other@example.com",
        )
        place = self._create_place(owner["id"])

        response = self.client.put(
            f"/api/v1/places/{place['id']}",
            json={"title": "Beach house"},
            headers=self._auth_headers(other_user["id"]),
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.get_json(),
            {"error": "Unauthorized action"},
        )
        self.assertEqual(facade.get_place(place["id"]).title, "Flat")

    def test_place_list_and_nested_review_creation_routes(self):
        owner = self._create_user()
        reviewer = self._create_user(
            first_name="Review",
            last_name="Author",
            email="reviewer@example.com",
        )
        place = self._create_place(owner["id"])

        list_response = self.client.get("/api/v1/places/")
        review_response = self.client.post(
            f"/api/v1/places/{place['id']}/reviews",
            json={
                "text": "Great stay",
                "rating": 5,
            },
            headers=self._auth_headers(reviewer["id"]),
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(
            [item["id"] for item in list_response.get_json()],
            [place["id"]],
        )
        self.assertEqual(review_response.status_code, 201)
        self.assertEqual(
            review_response.get_json(),
            {
                "id": review_response.get_json()["id"],
                "text": "Great stay",
                "rating": 5,
                "place_id": place["id"],
                "user_id": reviewer["id"],
            },
        )

    def test_amenity_and_review_delete_routes(self):
        owner = self._create_user()
        reviewer = self._create_user(
            first_name="Review",
            last_name="Author",
            email="reviewer@example.com",
        )
        amenity = self._create_amenity()
        place = self._create_place(owner["id"])
        review = self._create_review(place["id"], reviewer["id"])

        amenity_response = self.client.delete(
            f"/api/v1/amenities/{amenity['id']}"
        )
        review_response = self.client.delete(
            f"/api/v1/reviews/{review['id']}",
            headers=self._auth_headers(reviewer["id"]),
        )

        self.assertEqual(amenity_response.status_code, 200)
        self.assertEqual(
            amenity_response.get_json(),
            {"message": "Amenity deleted successfully"},
        )
        self.assertIsNone(facade.amenity_repo.get(amenity["id"]))

        self.assertEqual(review_response.status_code, 200)
        self.assertEqual(
            review_response.get_json(),
            {"message": "Review deleted successfully"},
        )
        self.assertIsNone(facade.review_repo.get(review["id"]))

    def test_place_details_include_nested_relationships(self):
        owner = self._create_user()
        reviewer = self._create_user(
            first_name="Review",
            last_name="Author",
            email="reviewer@example.com",
        )
        amenity = self._create_amenity()
        place = self._create_place(
            owner["id"],
            amenity_ids=[amenity["id"]],
        )
        review = self._create_review(place["id"], reviewer["id"])

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
                    "place_id": place["id"],
                    "user_id": reviewer["id"],
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
