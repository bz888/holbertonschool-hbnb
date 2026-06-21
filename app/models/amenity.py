from .base_model import BaseModel


class Amenity(BaseModel):
    """Amenity model."""

    def __init__(self, name):
        super().__init__()
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Amenity name must be a string")

        name = value.strip()
        if not name:
            raise ValueError("Amenity name is required")
        if len(name) > 50:
            raise ValueError(
                "Amenity name must be 50 characters or fewer"
            )

        self._name = name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
