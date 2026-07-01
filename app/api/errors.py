from utils.errors.amenity import AmenityNotFound
from utils.errors.place import PlaceNotFound
from utils.errors.review import OwnerCannotReviewOwnPlace, ReviewNotFound
from utils.errors.user import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    PasswordRequired,
    UserNotFound,
)


def _error_response(error):
    """Return the standard API error response body."""
    return {"error": str(error)}


def handle_not_found(error):
    """Convert missing domain resources into HTTP 404 responses."""
    return _error_response(error), 404


def handle_email_already_registered(error):
    """Convert duplicate email errors into HTTP 400 responses."""
    return _error_response(error), 400


def handle_invalid_credentials(error):
    """Convert failed authentication attempts into HTTP 401 responses."""
    return _error_response(error), 401


def handle_invalid_request(error):
    """Convert business-rule and validation errors into HTTP 400 responses."""
    return _error_response(error), 400


def register_error_handlers(api):
    """Register application-wide domain exception handlers."""
    for error_class in (
        AmenityNotFound,
        PlaceNotFound,
        ReviewNotFound,
        UserNotFound,
    ):
        api.errorhandler(error_class)(handle_not_found)

    api.errorhandler(EmailAlreadyRegistered)(
        handle_email_already_registered
    )
    api.errorhandler(InvalidCredentials)(handle_invalid_credentials)
    api.errorhandler(OwnerCannotReviewOwnPlace)(
        handle_invalid_request
    )
    api.errorhandler(PasswordRequired)(handle_invalid_request)
    api.errorhandler(ValueError)(handle_invalid_request)
