from utils.errors.amenity import AmenityNotFound
from utils.errors.place import PlaceNotFound
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
        email = user_data["email"]
        if self.user_repo.get_by_attribute("email", email):
            raise EmailAlreadyRegistered(email)

        user = User(**user_data)
        return self.user_repo.add(user)

    def get_user(self, user_id):
        """Return a user by ID or raise UserNotFound."""
        user = self.user_repo.get(user_id)
        if user is None:
            raise UserNotFound(user_id)
        return user

    def get_user_by_email(self, email):
        """Return the user with the given email, if one exists."""
        return self.user_repo.get_by_attribute("email", email)

    def get_all_users(self):
        """Return all users."""
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data) -> User:
        """Update and return a user."""
        user = self.user_repo.get(user_id)
        if user is None:
            raise UserNotFound(user_id)

        if "email" in user_data:
            email = user_data["email"]
            existing_user = self.user_repo.get_by_attribute(
                "email",
                email,
            )

            if existing_user and existing_user.id != user.id:
                raise EmailAlreadyRegistered(email)

        updated_user = self.user_repo.update(user_id, user_data)

        if updated_user is None:
            raise UserNotFound(user_id)

        return updated_user

    def delete_user(self, user_id):
        """Delete a user or raise UserNotFound."""
        user = self.user_repo.get(user_id)
        if user is None:
            raise UserNotFound(user_id)

        return self.user_repo.delete(user_id)

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
            amenity = Amenity(name=name.strip())
            amenity.id = amenity_id
            self.amenity_repo.add(amenity)

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
            raise ValueError("owner does not exist")

        amenity_ids = data.pop("amenity_ids", [])
        amenities = []
        for amenity_id in amenity_ids:
            amenity = self.amenity_repo.get(amenity_id)
            if amenity is None:
                raise ValueError(
                    f"amenity does not exist: {amenity_id}"
                )
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
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        data = place_data.copy()
        place = self.place_repo.get(place_id)
        if place is None:
            raise PlaceNotFound(place_id)

        if "owner_id" in data:
            owner = self.user_repo.get(data.pop("owner_id"))
            if owner is None:
                raise ValueError("owner does not exist")
            data["owner"] = owner

        if "amenity_ids" in data:
            amenities = []
            for amenity_id in data.pop("amenity_ids"):
                amenity = self.amenity_repo.get(amenity_id)
                if amenity is None:
                    raise ValueError(
                        f"amenity does not exist: {amenity_id}"
                    )
                amenities.append(amenity)
            data["amenities"] = amenities

        if "amenities" in data:
            place.amenities = []
            for amenity in data.pop("amenities"):
                place.add_amenity(amenity)

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
            raise ValueError("user does not exist")

        data.pop("place_id")
        data.pop("user_id")
        review = Review(place=place, user=user, **data)

        place.add_review(review)
        user.add_review(review)
        return self.review_repo.add(review)

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        if self.place_repo.get(place_id) is None:
            raise PlaceNotFound(place_id)

        return [
            review
            for review in self.review_repo.get_all()
            if review.place.id == place_id
        ]

    def update_review(self, review_id, review_data):
        data = review_data.copy()

        if "place_id" in data:
            place = self.place_repo.get(data.pop("place_id"))
            if place is None:
                raise ValueError("place does not exist")
            data["place"] = place

        if "user_id" in data:
            user = self.user_repo.get(data.pop("user_id"))
            if user is None:
                raise ValueError("user does not exist")
            data["user"] = user

        return self.review_repo.update(review_id, data)

    def delete_review(self, review_id):
        return self.review_repo.delete(review_id)
