import re

from extensions import bcrypt
from .base_model import BaseModel

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import validates


class User(BaseModel):
    """User model."""
    __tablename__ = "user"
    
    EMAIL_PATTERN = re.compile(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    
    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
    )

    password: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    places: Mapped[list["Place"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    reviews: Mapped[list["Review"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @validates("email")
    def validate_email(self, key, value):
        value = value.strip().lower()

        if not self.EMAIL_PATTERN.fullmatch(value):
            raise ValueError("Invalid email")

        return value

    def __init__(
        self,
        first_name,
        last_name,
        email,
        password=None,
        is_admin=False,
        is_active=True,
    ):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
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
