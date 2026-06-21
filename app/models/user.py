import re

from .base_model import BaseModel
import re

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


class User(BaseModel):
    """User model."""

    EMAIL_PATTERN = re.compile(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    def __init__(
        self,
        first_name,
        last_name,
        email,
        is_admin=False,
        is_active=True,
    ):
        super().__init__()

        if not first_name or not first_name.strip():
            raise ValueError("first_name cannot be empty")
        if not last_name or not last_name.strip():
            raise ValueError("last_name cannot be empty")
        if not email or not email.strip():
            raise ValueError("email cannot be empty")
        if not re.match(EMAIL_REGEX, email):
            raise ValueError("invalid email")

        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.is_active = is_active
        self.places = []
        self.reviews = []

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        self._first_name = self._validate_name(
            value,
            "First name",
        )

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        self._last_name = self._validate_name(
            value,
            "Last name",
        )

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = self.normalize_email(value)

    @classmethod
    def normalize_email(cls, value):
        """Validate and normalize an email address."""
        if not isinstance(value, str):
            raise ValueError("Email must be a string")

        email = value.strip().lower()
        if not cls.EMAIL_PATTERN.fullmatch(email):
            raise ValueError("Email must be a valid email address")

        return email

    @staticmethod
    def _validate_name(value, field_name):
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")

        name = value.strip()
        if not name:
            raise ValueError(f"{field_name} is required")
        if len(name) > 50:
            raise ValueError(
                f"{field_name} must be 50 characters or fewer"
            )

        return name

    def add_place(self, place):
        """Add a place owned by the user."""
        self.places.append(place)

    def add_review(self, review):
        """Add a review written by the user."""
        self.reviews.append(review)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
