from .base_model import BaseModel


class Place(BaseModel):
    """Place model."""

    def __init__(self, title, description, price, latitude, longitude, owner):
        super().__init__()

        if not title or not title.strip():
            raise ValueError("title cannot be empty")

        if price is None:
            raise ValueError("price is required")
        if not isinstance(price, (int, float)):
            raise ValueError("price must be a number")
        if price <= 0:
            raise ValueError("price must be a positive number")

        if latitude is None:
            raise ValueError("latitude is required")
        if not isinstance(latitude, (int, float)):
            raise ValueError("latitude must be a number")
        if latitude < -90 or latitude > 90:
            raise ValueError("latitude must be between -90 and 90")

        if longitude is None:
            raise ValueError("longitude is required")
        if not isinstance(longitude, (int, float)):
            raise ValueError("longitude must be a number")
        if longitude < -180 or longitude > 180:
            raise ValueError("longitude must be between -180 and 180")

        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        self.reviews = []
        self.amenities = []

    def add_review(self, review):
        """Add a review to the place."""
        self.reviews.append(review)

    def add_amenity(self, amenity):
        """Add an amenity to the place."""
        self.amenities.append(amenity)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "owner_id": self.owner.id,
            "amenities": [amenity.id for amenity in self.amenities],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
