class EmailAlreadyRegistered(Exception):
    """Raised when attempting to register an existing email."""

    def __init__(self, email=None):
        super().__init__("Email already registered")


class EmailAlreadyInUse(Exception):
    """Raised when a user update would duplicate an email address."""

    def __init__(self):
        super().__init__("Email already in use")


class AdminPrivilegesRequired(Exception):
    """Raised when a non-admin attempts an administrator-only action."""

    def __init__(self):
        super().__init__("Admin privileges required")


class PasswordRequired(Exception):
    """Raised when attempting to register a user without a password."""

    def __init__(self):
        super().__init__("Password is required")


class InvalidCredentials(Exception):
    """Raised when authentication credentials are incorrect."""

    def __init__(self):
        super().__init__("Invalid credentials")


class RestrictedUserFieldUpdate(Exception):
    """Raised when restricted user fields are updated through this endpoint."""

    def __init__(self):
        super().__init__("You cannot modify email or password.")


class UserNotFound(Exception):
    def __init__(self, user_id):
        super().__init__(f"User '{user_id}' not found")
