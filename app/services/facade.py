from models.amenity import Amenity
from models.place import Place
from models.review import Review
from models.user import User
from persistence.repository import InMemoryRepository


class HBnBFacade:
    """Facade that coordinates models and in-memory repositories."""

    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    def create_user(self, user_data):
        if self.user_repo.get_by_attribute("email", user_data["email"]):
            raise ValueError("email is already registered")

        user = User(**user_data)
        return self.user_repo.add(user)

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute("email", email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        if "email" in user_data:
            existing = self.user_repo.get_by_attribute("email", user_data["email"])
            if existing and existing.id != user_id:
                raise ValueError("email is already registered")
        return self.user_repo.update(user_id, user_data)

    def delete_user(self, user_id):
        return self.user_repo.delete(user_id)

    def create_amenity(self, amenity_data):
        amenity = Amenity(**amenity_data)
        return self.amenity_repo.add(amenity)

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        return self.amenity_repo.update(amenity_id, amenity_data)

    def delete_amenity(self, amenity_id):
        return self.amenity_repo.delete(amenity_id)

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
                raise ValueError(f"amenity does not exist: {amenity_id}")
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
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        data = place_data.copy()

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
                    raise ValueError(f"amenity does not exist: {amenity_id}")
                amenities.append(amenity)
            data["amenities"] = amenities

        place = self.place_repo.get(place_id)
        if place is None:
            return None

        if "amenities" in data:
            place.amenities = []
            for amenity in data.pop("amenities"):
                place.add_amenity(amenity)

        return self.place_repo.update(place_id, data)

    def delete_place(self, place_id):
        return self.place_repo.delete(place_id)

    def create_review(self, review_data):
        data = review_data.copy()
        place = self.place_repo.get(data["place_id"])
        if place is None:
            raise ValueError("place does not exist")

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
        return [
            review for review in self.review_repo.get_all() if review.place.id == place_id
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
