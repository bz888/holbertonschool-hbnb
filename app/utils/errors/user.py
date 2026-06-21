class EmailAlreadyRegistered(Exception):
    """Raised when attempting to register an existing email."""

    def __init__(self, email=None):
        message = (
            f"Email '{email}' is already registered"
            if email
            else "Email is already registered"
        )
        super().__init__(message)

class UserNotFound(Exception):
    def __init__(self, user_id):
        super().__init__(f"User '{user_id}' not found")