import re

from extensions import bcrypt
from .base_model import BaseModel

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates


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

    @validates("first_name", "last_name")
    def validate_name(self, key, value):
        if not isinstance(value, str):
            raise ValueError(f"{key} must be a string")

        value = value.strip()

        if not value:
            raise ValueError(f"{key} is required")

        if len(value) > 50:
            raise ValueError(f"{key} must be 50 characters or fewer")

        return value

    @validates("email")
    def validate_email(self, key, value):
        if not isinstance(value, str):
            raise ValueError("Email must be a string")

        value = value.strip().lower()

        if not self.EMAIL_PATTERN.fullmatch(value):
            raise ValueError("Invalid email")

        return value

    def add_place(self, place):
        self.places.append(place)

    def add_review(self, review):
        self.reviews.append(review)

    def hash_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def verify_password(self, password):
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