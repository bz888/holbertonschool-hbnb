from .base_model import BaseModel


class Review(BaseModel):
    """Review model."""

    def __init__(self, text, rating, place, user):
        super().__init__()
        self.text = text
        self.rating = rating
        self.place = place
        self.user = user

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if not isinstance(value, str):
            raise ValueError("Review text must be a string")

        text = value.strip()
        if not text:
            raise ValueError("Review text is required")

        self._text = text

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or not 1 <= value <= 5
        ):
            raise ValueError(
                "Review rating must be an integer from 1 to 5"
            )

        self._rating = value

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "rating": self.rating,
            "place_id": self.place.id,
            "user_id": self.user.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
