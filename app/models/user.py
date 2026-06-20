from .base_model import BaseModel


class User(BaseModel):
    """User model."""

    def __init__(
        self,
        first_name,
        last_name,
        email,
        is_admin=False,
        is_active=True,
    ):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.is_active = is_active
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
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
