import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.errors import (
    handle_email_already_registered,
    handle_invalid_credentials,
    handle_invalid_request,
    handle_not_found,
    register_error_handlers,
)
from utils.errors.amenity import AmenityNotFound
from utils.errors.place import PlaceNotFound
from utils.errors.review import OwnerCannotReviewOwnPlace, ReviewNotFound
from utils.errors.user import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    PasswordRequired,
    UserNotFound,
)


class FakeApi:
    def __init__(self):
        self.handlers = {}

    def errorhandler(self, error_class):
        def register(handler):
            self.handlers[error_class] = handler
            return handler

        return register


class TestApiErrorHandlers(unittest.TestCase):
    def test_registers_all_application_errors(self):
        api = FakeApi()

        register_error_handlers(api)

        self.assertEqual(
            set(api.handlers),
            {
                AmenityNotFound,
                PlaceNotFound,
                ReviewNotFound,
                UserNotFound,
                EmailAlreadyRegistered,
                InvalidCredentials,
                PasswordRequired,
                OwnerCannotReviewOwnPlace,
                ValueError,
            },
        )

    def test_not_found_handler_returns_404(self):
        body, status = handle_not_found(PlaceNotFound("missing"))

        self.assertEqual(body, {"error": "Place 'missing' not found"})
        self.assertEqual(status, 404)

    def test_duplicate_email_handler_returns_400(self):
        body, status = handle_email_already_registered(
            EmailAlreadyRegistered("ada@example.com")
        )

        self.assertEqual(
            body,
            {"error": "Email 'ada@example.com' is already registered"},
        )
        self.assertEqual(status, 400)

    def test_invalid_credentials_handler_returns_401(self):
        body, status = handle_invalid_credentials(InvalidCredentials())

        self.assertEqual(body, {"error": "Invalid credentials"})
        self.assertEqual(status, 401)

    def test_invalid_request_handler_returns_400(self):
        body, status = handle_invalid_request(
            OwnerCannotReviewOwnPlace()
        )

        self.assertEqual(
            body,
            {"error": "Owners cannot review their own place"},
        )
        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main()
