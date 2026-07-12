import sys
import unittest
from datetime import timedelta
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
        self.admin = facade.get_user_by_email("admin@example.com")
        self.admin_headers = self._auth_headers(
            self.admin.id,
            is_admin=True,
        )

    def _auth_headers(self, user_id, is_admin=False, expires_delta=None):
        token_args = {
            "identity": user_id,
            "additional_claims": {"is_admin": is_admin},
        }
        if expires_delta is not None:
            token_args["expires_delta"] = expires_delta

        with self.app.app_context():
            token = create_access_token(**token_args)

        return {"Authorization": f"Bearer {token}"}

    def _tampered_auth_headers(self, user_id):
        token = self._auth_headers(user_id)["Authorization"].split(" ", 1)[1]
        header, payload, signature = token.split(".")
        replacement = "a" if signature[0] != "a" else "b"
        tampered_signature = replacement + signature[1:]
        tampered_token = ".".join((header, payload, tampered_signature))
        return {"Authorization": f"Bearer {tampered_token}"}

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
            headers=self.admin_headers,
        )
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def _create_amenity(self, name="Wi-Fi"):
        response = self.client.post(
            "/api/v1/amenities/",
            json={"name": name},
            headers=self.admin_headers,
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

    def _protected_write_route_responses(
        self,
        owner_id,
        place_id,
        review_id,
        headers=None,
    ):
        request_options = {}
        if headers is not None:
            request_options["headers"] = headers

        return (
            (
                "POST /api/v1/places/",
                self.client.post(
                    "/api/v1/places/",
                    json={
                        "title": "New flat",
                        "price": 100,
                        "latitude": 0,
                        "longitude": 0,
                    },
                    **request_options,
                ),
            ),
            (
                "PUT /api/v1/places/<place_id>",
                self.client.put(
                    f"/api/v1/places/{place_id}",
                    json={"title": "Updated flat"},
                    **request_options,
                ),
            ),
            (
                "POST /api/v1/reviews/",
                self.client.post(
                    "/api/v1/reviews/",
                    json={
                        "text": "Great stay",
                        "rating": 5,
                        "place_id": place_id,
                    },
                    **request_options,
                ),
            ),
            (
                "POST /api/v1/places/<place_id>/reviews",
                self.client.post(
                    f"/api/v1/places/{place_id}/reviews",
                    json={
                        "text": "Great stay",
                        "rating": 5,
                    },
                    **request_options,
                ),
            ),
            (
                "PUT /api/v1/reviews/<review_id>",
                self.client.put(
                    f"/api/v1/reviews/{review_id}",
                    json={"rating": 4},
                    **request_options,
                ),
            ),
            (
                "DELETE /api/v1/reviews/<review_id>",
                self.client.delete(
                    f"/api/v1/reviews/{review_id}",
                    **request_options,
                ),
            ),
            (
                "PUT /api/v1/users/<user_id>",
                self.client.put(
                    f"/api/v1/users/{owner_id}",
                    json={"first_name": "Updated"},
                    **request_options,
                ),
            ),
        )

    def test_not_found_and_validation_errors_use_global_handlers(self):
        amenity = self.client.post(
            "/api/v1/amenities/",
            json={"name": "Wi-Fi"},
            headers=self.admin_headers,
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
                    headers=self.admin_headers,
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
                    headers=self.admin_headers,
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
                    headers=self.admin_headers,
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
                    headers=self.admin_headers,
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
            headers=self.admin_headers,
        )
        duplicate_response = self.client.post(
            "/api/v1/users/",
            json=user_data,
            headers=self.admin_headers,
        )

        self.assertEqual(user_response.status_code, 201)
        self.assertEqual(duplicate_response.status_code, 400)
        self.assertEqual(
            duplicate_response.get_json(),
            {"error": "Email already registered"},
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
            {"error": "You cannot review your own place."},
        )

    def test_duplicate_review_attempt_returns_bad_request(self):
        owner = self._create_user()
        reviewer = self._create_user(
            first_name="Review",
            last_name="Author",
            email="reviewer@example.com",
        )
        place = self._create_place(owner["id"])
        first_review = self._create_review(place["id"], reviewer["id"])

        response = self.client.post(
            f"/api/v1/places/{place['id']}/reviews",
            json={
                "text": "Second review",
                "rating": 4,
            },
            headers=self._auth_headers(reviewer["id"]),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {"error": "You have already reviewed this place."},
        )
        self.assertEqual(
            [review.id for review in facade.get_all_reviews()],
            [first_review["id"]],
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

        for route, response in self._protected_write_route_responses(
            owner["id"],
            place["id"],
            review["id"],
        ):
            with self.subTest(route=route):
                self.assertEqual(response.status_code, 401)
                self.assertEqual(
                    response.get_json(),
                    {"msg": "Missing Authorization Header"},
                )

    def test_jwt_protected_write_routes_reject_invalid_tokens(self):
        owner = self._create_user()
        reviewer = self._create_user(
            first_name="Review",
            last_name="Author",
            email="reviewer@example.com",
        )
        place = self._create_place(owner["id"])
        review = self._create_review(place["id"], reviewer["id"])

        token_cases = (
            (
                "malformed",
                {"Authorization": "Bearer not-a-jwt"},
            ),
            (
                "invalid_signature",
                self._tampered_auth_headers(owner["id"]),
            ),
            (
                "expired",
                self._auth_headers(
                    owner["id"],
                    expires_delta=timedelta(seconds=-1),
                ),
            ),
        )

        for token_case, headers in token_cases:
            for route, response in self._protected_write_route_responses(
                owner["id"],
                place["id"],
                review["id"],
                headers=headers,
            ):
                with self.subTest(token=token_case, route=route):
                    self.assertIn(response.status_code, (401, 422))
                    self.assertIn("msg", response.get_json())

        self.assertEqual(facade.get_place(place["id"]).title, "Flat")
        self.assertIsNotNone(facade.review_repo.get(review["id"]))
        self.assertEqual(facade.get_user(owner["id"]).first_name, "Owner")

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
            headers=self.admin_headers,
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

    def test_user_update_allows_own_user_token(self):
        user = self._create_user()

        response = self.client.put(
            f"/api/v1/users/{user['id']}",
            json={
                "first_name": "Augusta",
                "last_name": "Byron",
            },
            headers=self._auth_headers(user["id"]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["first_name"], "Augusta")
        self.assertEqual(response.get_json()["last_name"], "Byron")

        stored_user = facade.get_user(user["id"])
        self.assertEqual(stored_user.first_name, "Augusta")
        self.assertEqual(stored_user.last_name, "Byron")

    def test_user_update_rejects_other_user_token(self):
        user = self._create_user()
        other_user = self._create_user(
            first_name="Other",
            last_name="User",
            email="other-user@example.com",
        )

        response = self.client.put(
            f"/api/v1/users/{user['id']}",
            json={"first_name": "Augusta"},
            headers=self._auth_headers(other_user["id"]),
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.get_json(),
            {"error": "Admin privileges required"},
        )
        self.assertEqual(facade.get_user(user["id"]).first_name, "Owner")

    def test_user_update_rejects_email_change(self):
        user = self._create_user()

        response = self.client.put(
            f"/api/v1/users/{user['id']}",
            json={"email": "new@example.com"},
            headers=self._auth_headers(user["id"]),
        )

        stored_user = facade.get_user(user["id"])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.get_json(),
            {"error": "Admin privileges required"},
        )
        self.assertEqual(stored_user.email, "owner@example.com")

    def test_user_update_rejects_password_change(self):
        user = self._create_user()

        response = self.client.put(
            f"/api/v1/users/{user['id']}",
            json={"password": "new-password"},
            headers=self._auth_headers(user["id"]),
        )

        stored_user = facade.get_user(user["id"])
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.get_json(),
            {"error": "Admin privileges required"},
        )
        self.assertTrue(stored_user.verify_password("test-password"))

    def test_admin_only_user_and_amenity_routes_enforce_claim(self):
        user = self._create_user()
        amenity = self._create_amenity()
        regular_headers = self._auth_headers(user["id"])
        with self.app.app_context():
            token_without_admin_claim = create_access_token(
                identity=user["id"]
            )
        missing_claim_headers = {
            "Authorization": f"Bearer {token_without_admin_claim}"
        }

        requests = (
            self.client.post(
                "/api/v1/users/",
                json={
                    "first_name": "New",
                    "last_name": "User",
                    "email": "new@example.com",
                    "password": "test-password",
                },
            ),
            self.client.post(
                "/api/v1/amenities/",
                json={"name": "Pool"},
            ),
            self.client.put(
                f"/api/v1/amenities/{amenity['id']}",
                json={"name": "Parking"},
            ),
        )

        for response in requests:
            self.assertEqual(response.status_code, 401)

        regular_requests = (
            self.client.post(
                "/api/v1/users/",
                json={
                    "first_name": "New",
                    "last_name": "User",
                    "email": "new@example.com",
                    "password": "test-password",
                },
                headers=regular_headers,
            ),
            self.client.post(
                "/api/v1/amenities/",
                json={"name": "Pool"},
                headers=regular_headers,
            ),
            self.client.put(
                f"/api/v1/amenities/{amenity['id']}",
                json={"name": "Parking"},
                headers=regular_headers,
            ),
        )

        for response in regular_requests:
            self.assertEqual(response.status_code, 403)
            self.assertEqual(
                response.get_json(),
                {"error": "Admin privileges required"},
            )

        missing_claim_response = self.client.post(
            "/api/v1/amenities/",
            json={"name": "Sauna"},
            headers=missing_claim_headers,
        )
        self.assertEqual(missing_claim_response.status_code, 403)
        self.assertEqual(
            missing_claim_response.get_json(),
            {"error": "Admin privileges required"},
        )

    def test_admin_updates_another_users_email_and_password(self):
        user = self._create_user()

        response = self.client.put(
            f"/api/v1/users/{user['id']}",
            json={
                "email": "updated@example.com",
                "password": "updated-password",
            },
            headers=self.admin_headers,
        )

        self.assertEqual(response.status_code, 200)
        stored_user = facade.get_user(user["id"])
        self.assertEqual(stored_user.email, "updated@example.com")
        self.assertTrue(stored_user.verify_password("updated-password"))

    def test_admin_user_update_rejects_duplicate_email(self):
        user = self._create_user()
        other_user = self._create_user(
            first_name="Other",
            last_name="User",
            email="other@example.com",
        )

        response = self.client.put(
            f"/api/v1/users/{user['id']}",
            json={"email": " OTHER@EXAMPLE.COM "},
            headers=self.admin_headers,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {"error": "Email already in use"},
        )
        self.assertEqual(
            facade.get_user(user["id"]).email,
            "owner@example.com",
        )
        self.assertEqual(
            facade.get_user(other_user["id"]).email,
            "other@example.com",
        )

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
            headers=self.admin_headers,
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
            headers=self.admin_headers,
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
            headers=self.admin_headers,
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
                        "Allowed fields: first_name, last_name"
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
                    headers=self.admin_headers,
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

    def test_admin_can_update_place_owned_by_another_user(self):
        owner = self._create_user()
        place = self._create_place(owner["id"])

        response = self.client.put(
            f"/api/v1/places/{place['id']}",
            json={"title": "Admin updated"},
            headers=self.admin_headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            facade.get_place(place["id"]).title,
            "Admin updated",
        )

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

    def test_review_update_and_delete_by_non_author_return_forbidden(self):
        owner = self._create_user()
        reviewer = self._create_user(
            first_name="Review",
            last_name="Author",
            email="reviewer@example.com",
        )
        other_user = self._create_user(
            first_name="Other",
            last_name="User",
            email="other-review@example.com",
        )
        place = self._create_place(owner["id"])
        review = self._create_review(place["id"], reviewer["id"])

        update_response = self.client.put(
            f"/api/v1/reviews/{review['id']}",
            json={"rating": 4},
            headers=self._auth_headers(other_user["id"]),
        )
        delete_response = self.client.delete(
            f"/api/v1/reviews/{review['id']}",
            headers=self._auth_headers(other_user["id"]),
        )

        for response in (update_response, delete_response):
            self.assertEqual(response.status_code, 403)
            self.assertEqual(
                response.get_json(),
                {"error": "Unauthorized action"},
            )

        stored_review = facade.get_review(review["id"])
        self.assertEqual(stored_review.rating, 5)
        self.assertIn(stored_review, stored_review.user.reviews)
        self.assertIn(stored_review, stored_review.place.reviews)

    def test_admin_can_update_and_delete_another_users_review(self):
        owner = self._create_user()
        reviewer = self._create_user(
            first_name="Review",
            last_name="Author",
            email="reviewer@example.com",
        )
        place = self._create_place(owner["id"])
        review = self._create_review(place["id"], reviewer["id"])

        update_response = self.client.put(
            f"/api/v1/reviews/{review['id']}",
            json={"rating": 4},
            headers=self.admin_headers,
        )
        delete_response = self.client.delete(
            f"/api/v1/reviews/{review['id']}",
            headers=self.admin_headers,
        )

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 200)
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
