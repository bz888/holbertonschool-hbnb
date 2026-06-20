from .base_model import BaseModel


class Place(BaseModel):
    """Place model."""

    def __init__(
        self,
        title,
        description,
        price,
        latitude,
        longitude,
        owner,
        is_active=True,
    ):
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        self.is_active = is_active
        self.reviews = []
        self.amenities = []

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not isinstance(value, str):
            raise ValueError("Place title must be a string")

        title = value.strip()
        if not title:
            raise ValueError("Place title is required")
        if len(title) > 100:
            raise ValueError(
                "Place title must be 100 characters or fewer"
            )

        self._title = title

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or value <= 0
        ):
            raise ValueError("Place price must be a positive number")

        self._price = value

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        self._latitude = self._validate_coordinate(
            value,
            "Latitude",
            -90,
            90,
        )

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        self._longitude = self._validate_coordinate(
            value,
            "Longitude",
            -180,
            180,
        )

    @staticmethod
    def _validate_coordinate(value, field_name, minimum, maximum):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not minimum <= value <= maximum
        ):
            raise ValueError(
                f"{field_name} must be between "
                f"{minimum} and {maximum}"
            )

        return value

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
            "is_active": self.is_active,
            "amenities": [amenity.id for amenity in self.amenities],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
