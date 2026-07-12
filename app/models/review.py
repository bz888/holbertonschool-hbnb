from .base_model import BaseModel
from extensions import db

from sqlalchemy.orm import validates


class Review(BaseModel):
    """Review model"""

    __tablename__ = 'reviews'

    text = db.Column(
        db.String(50),
        nullable=False
    )

    rating = db.Column(
        db.Integer,
        nullable=False,
    )

    user_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    place_id = db.Column(
        db.String(36),
        db.ForeignKey("places.id", ondelete="CASCADE"),
        nullable=False,
    )

    user = db.relationship(
        "User",
        back_populates="reviews",
    )

    place = db.relationship(
        "Place",
        back_populates="reviews",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "place_id",
            name="uq_review_user_place",
        ),
    )

    def __init__(
        self,
        text=None,
        rating=None,
        place=None,
        user=None,
        **kwargs,
    ):
        """Initialize a review with its place and author relationships."""
        from .place import Place
        from .user import User

        if not isinstance(place, Place):
            raise ValueError("Review place must be a Place")
        if not isinstance(user, User):
            raise ValueError("Review user must be a User")

        super().__init__(
            text=text,
            rating=rating,
            place=place,
            user=user,
            **kwargs,
        )

    @validates("text")
    def validate_text(self, key, value):
        if not isinstance(value, str):
            raise ValueError("Review text must be a string")

        value = value.strip()

        if not value:
            raise ValueError("Review text is required")

        if len(value) > 50:
            raise ValueError("Review text must be 50 characters or fewer")

        return value

    @validates("rating")
    def validate_rating(self, key, value):
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or not 1 <= value <= 5
        ):
            raise ValueError(
                "Review rating must be an integer from 1 to 5"
            )

        return value

    def to_dict(self):
        place_id = self.place_id
        if place_id is None and self.place is not None:
            place_id = self.place.id

        user_id = self.user_id
        if user_id is None and self.user is not None:
            user_id = self.user.id

        return {
            "id": self.id,
            "text": self.text,
            "rating": self.rating,
            "place_id": place_id,
            "user_id": user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
