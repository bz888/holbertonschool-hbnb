from .base_model import BaseModel
import re

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


class User(BaseModel):
    """User model."""

    def __init__(self, first_name, last_name, email, is_admin=False):
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
        self.places = []
        self.reviews = []

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
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
