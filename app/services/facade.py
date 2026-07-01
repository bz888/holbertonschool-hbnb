from utils.errors.amenity import AmenityNotFound
from utils.errors.place import PlaceNotFound
from utils.errors.review import OwnerCannotReviewOwnPlace, ReviewNotFound
from utils.errors.user import (
    EmailAlreadyRegistered,
    PasswordRequired,
    UserNotFound,
)
from models.amenity import Amenity
from models.place import Place
from models.review import Review
from models.user import User
from persistence.repository import InMemoryRepository

# validators
from validators.fields import validate_allowed_fields

ALLOWED_REVIEW_UPDATE_FIELDS = {"text", "rating"}
ALLOWED_USER_UPDATE_FIELDS = {"first_name", "last_name", "email"}
ALLOWED_AMENITY_UPDATE_FIELDS = {"name"}
ALLOWED_PLACE_UPDATE_FIELDS = {
    "title",
    "description",
    "price",
    "latitude",
    "longitude",
    "amenity_ids",
}


class HBnBFacade:
    """Coordinate models and in-memory repositories."""

    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    def create_user(self, user_data):
        """Create and store a user."""
        data = user_data.copy()
        email = User.normalize_email(data["email"])
        existing_user = self.user_repo.find_one(
            email=email,
            # is_active=True,
        )
        if existing_user:
            raise EmailAlreadyRegistered(email)

        password = data.pop("password", None)
        if password is None:
            raise PasswordRequired()

        data["email"] = email
        user = User(**data)
        user.hash_password(password)
        return self.user_repo.add(user)

    def get_user(self, user_id):
        """Return a user by ID or raise UserNotFound."""
        user = self.user_repo.get(user_id)
        if user is None:
            raise UserNotFound(user_id)
        return user

    def get_user_by_email(self, email):
        """Return the user with the given email, if one exists."""
        email = User.normalize_email(email)
        return self.user_repo.find_one(
            email=email,
            # is_active=True,
        )

    def get_all_users(self):
        """Return all users."""
        return self.user_repo.find_all(
            # is_active=True, future feature
        )

    def update_user(self, user_id, user_data) -> User:
        """Update and return a user."""
        user = self.user_repo.get(user_id)
        if user is None:
            raise UserNotFound(user_id)

        validate_allowed_fields(
            user_data,
            ALLOWED_USER_UPDATE_FIELDS,
            resource_name="user",
        )

        if "email" in user_data:
            email = User.normalize_email(user_data["email"])
            existing_user = self.user_repo.find_one(
                email=email,
                # is_active=True,
            )

            if existing_user and existing_user.id != user.id:
                raise EmailAlreadyRegistered(email)

            user_data = user_data.copy()
            user_data["email"] = email

        updated_user = self.user_repo.update(user_id, user_data)

        if updated_user is None:
            raise UserNotFound(user_id)

        return updated_user

    def soft_delete_user(self, user_id):
        """Deactivate a user and their places while preserving reviews."""
        user = self.user_repo.get(user_id)
        if user is None:
            raise UserNotFound(user_id)

        user.is_active = False
        user.save()

        for place in self.place_repo.find_all(
            owner=user,
            # is_active=True, future feature
        ):
            place.is_active = False
            place.save()

        return user

    def delete_user(self, user_id):
        """Permanently delete a user from the repository."""
        user = self.user_repo.delete(user_id)
        if user is None:
            raise UserNotFound(user_id)

        # TODO: Replace hard deletion with soft deletion or anonymization
        # where reviews and places must retain a valid user reference.
        return user

    def create_amenity(self, amenity_data):
        name = amenity_data.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Amenity name must be a non-empty string")

        amenity = Amenity(name=name.strip())
        return self.amenity_repo.add(amenity)

    def get_amenity(self, amenity_id):
        amenity = self.amenity_repo.get(amenity_id)
        if amenity is None:
            raise AmenityNotFound(amenity_id)
        return amenity

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        validate_allowed_fields(
            amenity_data,
            ALLOWED_AMENITY_UPDATE_FIELDS,
            resource_name="amenity",
        )

        amenity = self.amenity_repo.get(amenity_id)
        if amenity is None:
            raise AmenityNotFound(amenity_id)

        name = amenity_data.get("name")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Amenity name must be a non-empty string")

        updated_amenity = self.amenity_repo.update(
            amenity_id,
            {"name": name.strip()},
        )

        if updated_amenity is None:
            raise AmenityNotFound(amenity_id)

        return updated_amenity

    def delete_amenity(self, amenity_id):
        amenity = self.amenity_repo.delete(amenity_id)
        if amenity is None:
            raise AmenityNotFound(amenity_id)
        return amenity

    def create_place(self, place_data):
        data = place_data.copy()
        owner = self.user_repo.get(data["owner_id"])
        if owner is None:
            raise UserNotFound(data["owner_id"])

        amenity_ids = data.pop("amenity_ids", [])
        amenities = []
        for amenity_id in amenity_ids:
            amenity = self.amenity_repo.get(amenity_id)
            if amenity is None:
                raise AmenityNotFound(amenity_id)
            amenities.append(amenity)

        data.pop("owner_id")
        place = Place(
            data["title"],
            data.get("description", ""),
            data["price"],
            data["latitude"],
            data["longitude"],
            owner,
        )

        for amenity in amenities:
            place.add_amenity(amenity)

        owner.add_place(place)
        return self.place_repo.add(place)

    def get_place(self, place_id):
        place = self.place_repo.get(place_id)
        if place is None:
            raise PlaceNotFound(place_id)
        return place

    def get_all_places(self):
        return self.place_repo.find_all(
            # is_active=True, future feature
        )

    def update_place(self, place_id, place_data):

        validate_allowed_fields(
            place_data,
            ALLOWED_PLACE_UPDATE_FIELDS,
            resource_name="place",
        )

        data = place_data.copy()

        place = self.place_repo.get(place_id)
        if place is None:
            raise PlaceNotFound(place_id)

        if "amenity_ids" in data:
            amenities = []
            for amenity_id in data.pop("amenity_ids"):
                amenity = self.amenity_repo.get(amenity_id)
                if amenity is None:
                    raise AmenityNotFound(amenity_id)
                amenities.append(amenity)
            data["amenities"] = amenities

        updated_place = self.place_repo.update(place_id, data)
        if updated_place is None:
            raise PlaceNotFound(place_id)
        return updated_place

    def delete_place(self, place_id):
        place = self.place_repo.delete(place_id)
        if place is None:
            raise PlaceNotFound(place_id)

        return place

    def create_review(self, review_data):
        data = review_data.copy()
        place = self.place_repo.get(data["place_id"])
        if place is None:
            raise PlaceNotFound(data["place_id"])

        user = self.user_repo.get(data["user_id"])
        if user is None:
            raise UserNotFound(data["user_id"])

        if user.id == place.owner.id:
            raise OwnerCannotReviewOwnPlace()

        data.pop("place_id")
        data.pop("user_id")
        review = Review(place=place, user=user, **data)

        place.add_review(review)
        user.add_review(review)
        return self.review_repo.add(review)

    def get_review(self, review_id):
        review = self.review_repo.get(review_id)
        if review is None:
            raise ReviewNotFound(review_id)
        return review

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        place = self.place_repo.get(place_id)
        if place is None:
            raise PlaceNotFound(place_id)

        return self.review_repo.find_all(place=place)

    def get_reviews_by_user(self, user_id):
        user = self.user_repo.get(user_id)
        if user is None:
            raise UserNotFound(user_id)

        return self.review_repo.find_all(user=user)

    def update_review(self, review_id, review_data):
        data = review_data.copy()

        review = self.review_repo.get(review_id)
        if review is None:
            raise ReviewNotFound(review_id)

        validate_allowed_fields(
            data,
            ALLOWED_REVIEW_UPDATE_FIELDS,
            resource_name="review",
        )

        updated_review = self.review_repo.update(review_id, data)
        if updated_review is None:
            raise ReviewNotFound(review_id)

        return updated_review

    def delete_review(self, review_id):
        review = self.review_repo.delete(review_id)
        if review is None:
            raise ReviewNotFound(review_id)

        if review in review.place.reviews:
            review.place.reviews.remove(review)
        if review in review.user.reviews:
            review.user.reviews.remove(review)

        return review
