from utils.errors.amenity import AmenityNotFound
from utils.errors.place import PlaceNotFound
from utils.errors.review import OwnerCannotReviewOwnPlace, ReviewNotFound
from utils.errors.user import EmailAlreadyRegistered, UserNotFound
from models.amenity import Amenity
from models.place import Place
from models.review import Review
from models.user import User
from persistence.repository import InMemoryRepository


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
            is_active=True,
        )
        if existing_user:
            raise EmailAlreadyRegistered(email)

        data["email"] = email
        user = User(**data)
        return self.user_repo.add(user)

    def get_user(self, user_id):
        """Return a user by ID or raise UserNotFound."""
        user = self.user_repo.get(user_id)
        if user is None or not user.is_active:
            raise UserNotFound(user_id)
        return user

    def get_user_by_email(self, email):
        """Return the user with the given email, if one exists."""
        email = User.normalize_email(email)
        return self.user_repo.find_one(
            email=email,
            is_active=True,
        )

    def get_all_users(self):
        """Return all active users."""
        return self.user_repo.find_all(is_active=True)

    def update_user(self, user_id, user_data) -> User:
        """Update and return a user."""
        user = self.user_repo.get(user_id)
        if user is None or not user.is_active:
            raise UserNotFound(user_id)

        if "email" in user_data:
            email = User.normalize_email(user_data["email"])
            existing_user = self.user_repo.find_one(
                email=email,
                is_active=True,
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
        if user is None or not user.is_active:
            raise UserNotFound(user_id)

        user.is_active = False
        user.save()

        for place in self.place_repo.find_all(
            owner=user,
            is_active=True,
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
            raise ValueError(
                "Amenity name must be a non-empty string"
            )

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
        name = amenity_data.get("name")

        amenity = self.amenity_repo.get(amenity_id)
        if amenity is None:
            raise AmenityNotFound(amenity_id)

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
        if owner is None or not owner.is_active:
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
        if place is None or not place.is_active:
            raise PlaceNotFound(place_id)
        return place

    def get_all_places(self):
        return self.place_repo.find_all(is_active=True)

    def update_place(self, place_id, place_data):
        data = place_data.copy()
        place = self.place_repo.get(place_id)
        if place is None or not place.is_active:
            raise PlaceNotFound(place_id)

        if "owner_id" in data:
            owner_id = data.pop("owner_id")
            owner = self.user_repo.get(owner_id)
            if owner is None or not owner.is_active:
                raise UserNotFound(owner_id)
            data["owner"] = owner

        if "amenity_ids" in data:
            amenities = []
            for amenity_id in data.pop("amenity_ids"):
                amenity = self.amenity_repo.get(amenity_id)
                if amenity is None:
                    raise AmenityNotFound(amenity_id)
                amenities.append(amenity)
            data["amenities"] = amenities

        if "amenities" in data:
            place.amenities = []
            for amenity in data.pop("amenities"):
                place.add_amenity(amenity)

        if "owner" in data and data["owner"] is not place.owner:
            if place in place.owner.places:
                place.owner.places.remove(place)
            data["owner"].add_place(place)

        updated_place = self.place_repo.update(place_id, data)
        if updated_place is None:
            raise PlaceNotFound(place_id)
        return updated_place

    def delete_place(self, place_id):
        place = self.place_repo.get(place_id)
        if place is None or not place.is_active:
            raise PlaceNotFound(place_id)

        place.is_active = False
        place.save()
        return place

    def create_review(self, review_data):
        data = review_data.copy()
        place = self.place_repo.get(data["place_id"])
        if place is None or not place.is_active:
            raise PlaceNotFound(data["place_id"])

        user = self.user_repo.get(data["user_id"])
        if user is None or not user.is_active:
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
        if place is None or not place.is_active:
            raise PlaceNotFound(place_id)

        return self.review_repo.find_all(place=place)

    def get_reviews_by_user(self, user_id):
        user = self.user_repo.get(user_id)
        if user is None or not user.is_active:
            raise UserNotFound(user_id)

        return self.review_repo.find_all(user=user)

    def update_review(self, review_id, review_data):
        data = review_data.copy()
        review = self.review_repo.get(review_id)
        if review is None:
            raise ReviewNotFound(review_id)

        if "place_id" in data:
            place_id = data.pop("place_id")
            place = self.place_repo.get(place_id)
            if place is None or not place.is_active:
                raise PlaceNotFound(place_id)
        else:
            place = review.place

        if "user_id" in data:
            user_id = data.pop("user_id")
            user = self.user_repo.get(user_id)
            if user is None or not user.is_active:
                raise UserNotFound(user_id)
        else:
            user = review.user

        if user.id == place.owner.id:
            raise OwnerCannotReviewOwnPlace()

        if place is not review.place:
            if review in review.place.reviews:
                review.place.reviews.remove(review)
            place.add_review(review)
            data["place"] = place

        if user is not review.user:
            if review in review.user.reviews:
                review.user.reviews.remove(review)
            user.add_review(review)
            data["user"] = user

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
