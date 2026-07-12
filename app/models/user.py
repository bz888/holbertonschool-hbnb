import re

from extensions import bcrypt, db
from .base_model import BaseModel

from sqlalchemy.orm import validates


class User(BaseModel):
    """User model."""

    __tablename__ = 'users'

    EMAIL_PATTERN = re.compile(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    first_name = db.Column(
        db.String(50),
        nullable=False
    )

    last_name = db.Column(
        db.String(50),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False,
        unique=True
    )

    password = db.Column(
        db.String(128),
        nullable=False
    )

    is_admin = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
    )

    places = db.relationship(
        "Place",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    reviews = db.relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __init__(
        self,
        first_name=None,
        last_name=None,
        email=None,
        **kwargs,
    ):
        """Initialize a user with positional or keyword domain fields."""
        kwargs.setdefault("is_admin", False)
        kwargs.setdefault("is_active", True)
        super().__init__(
            first_name=first_name,
            last_name=last_name,
            email=email,
            **kwargs,
        )

    @validates("first_name")
    def validate_first_name(self, key, value):
        return self._validate_name(value, "First name")

    @validates("last_name")
    def validate_last_name(self, key, value):
        return self._validate_name(value, "Last name")

    @validates("email")
    def validate_email(self, key, value):
        return self.normalize_email(value)

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
        """Associate an owned place with this user."""
        if place not in self.places:
            self.places.append(place)

    def add_review(self, review):
        """Associate an authored review with this user."""
        if review not in self.reviews:
            self.reviews.append(review)

    def hash_password(self, password):
        """Hashes the password before storing it."""
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        return bcrypt.check_password_hash(self.password, password)

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
