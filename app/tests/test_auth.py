import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from flask import Flask

    from __init__ import create_app
    from api.v1.auth import Login, ProtectedResource
    from services import facade
    from services.facade import HBnBFacade
    from utils.errors.user import InvalidCredentials
except ModuleNotFoundError as error:
    if error.name not in {
        "flask",
        "flask_bcrypt",
        "flask_jwt_extended",
        "flask_restx",
    }:
        raise
    create_app = None
    facade = None
    Flask = None
    Login = None
    ProtectedResource = None
    HBnBFacade = None
    InvalidCredentials = None


@unittest.skipIf(
    create_app is None,
    "Flask dependencies are not installed",
)
class TestAuthUnit(unittest.TestCase):
    def setUp(self):
        self.request_app = Flask(__name__)

    def test_login_returns_token_with_user_identity_and_admin_claim(self):
        fake_user = Mock()
        fake_user.id = "user-123"
        fake_user.is_admin = True
        credentials = {
            "email": "admin@example.com",
            "password": "test-password",
        }

        with self.request_app.test_request_context(json=credentials):
            with patch(
                "api.v1.auth.facade.authenticate_user",
                return_value=fake_user,
            ) as authenticate_user, patch(
                "api.v1.auth.create_access_token",
                return_value="jwt-token",
            ) as create_access_token:
                body, status = Login().post()

        self.assertEqual(status, 200)
        self.assertEqual(body, {"access_token": "jwt-token"})
        authenticate_user.assert_called_once_with(credentials)
        create_access_token.assert_called_once_with(
            identity="user-123",
            additional_claims={"is_admin": True},
        )

    def test_facade_authenticate_user_rejects_invalid_credentials(self):
        test_facade = HBnBFacade()
        test_facade.create_user(
            {
                "first_name": "Auth",
                "last_name": "User",
                "email": "auth@example.com",
                "password": "test-password",
            }
        )

        with self.assertRaises(InvalidCredentials):
            test_facade.authenticate_user(
                {
                    "email": "auth@example.com",
                    "password": "wrong-password",
                }
            )

    def test_protected_response_uses_current_identity_and_admin_claim(self):
        with patch(
            "api.v1.auth.get_jwt_identity",
            return_value="user-123",
        ), patch(
            "api.v1.auth.get_jwt",
            return_value={"is_admin": False},
        ):
            body, status = ProtectedResource.get.__wrapped__(
                ProtectedResource()
            )

        self.assertEqual(status, 200)
        self.assertEqual(
            body,
            {
                "message": "Hello, user user-123",
                "is_admin": False,
            },
        )


@unittest.skipIf(
    create_app is None,
    "Flask dependencies are not installed",
)
class TestAuthIntegration(unittest.TestCase):
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

    def _create_user(self, email="auth@example.com", is_admin=False):
        response = self.client.post(
            "/api/v1/users/",
            json={
                "first_name": "Auth",
                "last_name": "User",
                "email": email,
                "password": "test-password",
            },
        )
        self.assertEqual(response.status_code, 201)

        user = facade.get_user_by_email(email)
        user.is_admin = is_admin

        return response.get_json()

    def test_login_token_allows_protected_request_with_expected_body(self):
        user = self._create_user(is_admin=True)

        login_response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "auth@example.com",
                "password": "test-password",
            },
        )

        self.assertEqual(login_response.status_code, 200)
        token = login_response.get_json()["access_token"]

        protected_response = self.client.get(
            "/api/v1/auth/protected",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(protected_response.status_code, 200)
        self.assertEqual(
            protected_response.get_json(),
            {
                "message": f"Hello, user {user['id']}",
                "is_admin": True,
            },
        )

    def test_login_rejects_bad_password(self):
        self._create_user()

        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "auth@example.com",
                "password": "wrong-password",
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.get_json(),
            {"error": "Invalid credentials"},
        )

    def test_login_rejects_extra_request_fields(self):
        self._create_user()

        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "auth@example.com",
                "password": "test-password",
                "is_admin": True,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {
                "error": (
                    "Invalid fields for login: is_admin. "
                    "Allowed fields: email, password"
                )
            },
        )

    def test_protected_requires_jwt(self):
        response = self.client.get("/api/v1/auth/protected")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.get_json(),
            {"msg": "Missing Authorization Header"},
        )


if __name__ == "__main__":
    unittest.main()
