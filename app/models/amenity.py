from extensions import db
from sqlalchemy.orm import validates

from .base_model import BaseModel


class Amenity(BaseModel):
    """Amenity model."""

    __tablename__ = "amenities"

    name = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    # places = db.relationship(
    #     "Place",
    #     secondary="place_amenities",
    #     back_populates="amenities",
    # )

    @validates("name")
    def validate_name(self, key, value):
        if not isinstance(value, str):
            raise ValueError("Amenity name must be a string")

        value = value.strip()

        if not value:
            raise ValueError("Amenity name is required")

        if len(value) > 50:
            raise ValueError(
                "Amenity name must be 50 characters or fewer"
            )

        return value

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }