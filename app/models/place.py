from .base_model import BaseModel
from extensions import db

from sqlalchemy.orm import validates


place_amenities = db.Table(
    "place_amenities",
    db.Column(
        "place_id",
        db.String(36),
        db.ForeignKey("places.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "amenity_id",
        db.String(36),
        db.ForeignKey("amenities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Place(BaseModel):
    """Place model."""

    __tablename__ = "places"

    title = db.Column(
        db.String(100),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    price = db.Column(
        db.Float,
        nullable=False,
    )

    latitude = db.Column(
        db.Float,
        nullable=False,
    )

    longitude = db.Column(
        db.Float,
        nullable=False,
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
    )

    owner_id = db.Column(
        db.String(36),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    owner = db.relationship(
        "User",
        back_populates="places",
    )

    reviews = db.relationship(
        "Review",
        back_populates="place",
        cascade="all, delete-orphan",
    )

    amenities = db.relationship(
        "Amenity",
        secondary=place_amenities,
        back_populates="places",
    )

    def __init__(
        self,
        title=None,
        description="",
        price=None,
        latitude=None,
        longitude=None,
        owner=None,
        **kwargs,
    ):
        """Initialize a place with its owning user relationship."""
        from .user import User

        if not isinstance(owner, User):
            raise ValueError("Place owner must be a User")

        kwargs.setdefault("is_active", True)
        super().__init__(
            title=title,
            description=description,
            price=price,
            latitude=latitude,
            longitude=longitude,
            owner=owner,
            **kwargs,
        )

    @validates("title")
    def validate_title(self, key, value):
        if not isinstance(value, str):
            raise ValueError("Place title must be a string")

        value = value.strip()

        if not value:
            raise ValueError("Place title is required")

        if len(value) > 100:
            raise ValueError(
                "Place title must be 100 characters or fewer"
            )

        return value

    @validates("price")
    def validate_price(self, key, value):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or value <= 0
        ):
            raise ValueError(
                "Place price must be a positive number"
            )

        return float(value)

    def add_review(self, review):
        """Associate a review with this place."""
        if review not in self.reviews:
            self.reviews.append(review)

    def add_amenity(self, amenity):
        """Associate an amenity with this place."""
        if amenity not in self.amenities:
            self.amenities.append(amenity)

    @validates("latitude")
    def validate_latitude(self, key, value):
        return self._validate_coordinate(
            value,
            "Latitude",
            -90,
            90,
        )

    @validates("longitude")
    def validate_longitude(self, key, value):
        return self._validate_coordinate(
            value,
            "Longitude",
            -180,
            180,
        )

    @staticmethod
    def _validate_coordinate(
        value,
        field_name,
        minimum,
        maximum,
    ):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not minimum <= value <= maximum
        ):
            raise ValueError(
                f"{field_name} must be between "
                f"{minimum} and {maximum}"
            )

        return float(value)

    def to_dict(self):
        owner_id = self.owner_id
        if owner_id is None and self.owner is not None:
            owner_id = self.owner.id

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "owner_id": owner_id,
            "is_active": self.is_active,
            "amenities": [amenity.id for amenity in self.amenities],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
