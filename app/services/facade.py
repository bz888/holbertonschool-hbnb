from utils.errors.amenity import AmenityNotFound
from utils.errors.place import PlaceNotFound, UnauthorizedAction
from utils.errors.review import (
    DuplicateReview,
    OwnerCannotReviewOwnPlace,
    ReviewNotFound,
)
from utils.errors.user import (
    AdminPrivilegesRequired,
    EmailAlreadyInUse,
    EmailAlreadyRegistered,
    InvalidCredentials,
    PasswordRequired,
    UserNotFound,
)
from extensions import db
from models.amenity import Amenity
from models.place import Place
from models.review import Review
from models.user import User

from persistence.user_repository import UserRepository
from persistence.amenity_repository import AmenityRepository
from persistence.review_repository import ReviewRepository
from persistence.place_repository import PlaceRepository

# validators
from validators.fields import validate_allowed_fields

ALLOWED_REVIEW_UPDATE_FIELDS = {"text", "rating"}
ALLOWED_LOGIN_FIELDS = {"email", "password"}
ALLOWED_USER_UPDATE_FIELDS = {"first_name", "last_name"}
ALLOWED_ADMIN_USER_UPDATE_FIELDS = {
    "first_name",
    "last_name",
    "email",
    "password",
}
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
    """Coordinate domain rules and SQLAlchemy repositories."""

    def __init__(self):
        self.user_repo = UserRepository()
        self.place_repo = PlaceRepository()
        self.review_repo = ReviewRepository()
        self.amenity_repo = AmenityRepository()

    def create_user(self, user_data, is_admin):
        """Create and store a user."""
        if not is_admin:
            raise AdminPrivilegesRequired()

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

    def authenticate_user(self, credentials):
        """Return the authenticated user or raise InvalidCredentials."""
        validate_allowed_fields(
            credentials,
            ALLOWED_LOGIN_FIELDS,
            resource_name="login",
        )

        user = self.get_user_by_email(credentials["email"])
        if not user or not user.verify_password(credentials["password"]):
            raise InvalidCredentials()

        return user

    def get_all_users(self):
        """Return all users."""
        return self.user_repo.find_all(
            # is_active=True, future feature
        )

    def update_user(
        self,
        user_id,
        user_data,
        current_user_id,
        is_admin,
    ) -> User:
        """Update and return a user."""
        user = self.user_repo.get(user_id)
        if user is None:
            raise UserNotFound(user_id)

        protected_fields = {"email", "password"} & set(user_data)
        if not is_admin and (
            user.id != current_user_id or protected_fields
        ):
            raise AdminPrivilegesRequired()

        validate_allowed_fields(
            user_data,
            (
                ALLOWED_ADMIN_USER_UPDATE_FIELDS
                if is_admin
                else ALLOWED_USER_UPDATE_FIELDS
            ),
            resource_name="user",
        )

        data = user_data.copy()
        if "email" in data:
            email = User.normalize_email(data["email"])
            existing_user = self.user_repo.find_one(email=email)
            if existing_user is not None and existing_user.id != user_id:
                raise EmailAlreadyInUse()
            data["email"] = email

        password = data.pop("password", None)
        if password is not None:
            user.hash_password(password)

        updated_user = self.user_repo.update(user_id, data)

        if updated_user is None:
            raise UserNotFound(user_id)

        return updated_user

    def soft_delete_user(self, user_id):
        """Deactivate a user and their places while preserving reviews."""
        user = self.user_repo.get(user_id)
        if user is None:
            raise UserNotFound(user_id)

        try:
            user.is_active = False
            for place in self.place_repo.find_all(owner_id=user.id):
                place.is_active = False
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return user

    def delete_user(self, user_id):
        """Permanently delete a user from the repository."""
        user = self.user_repo.delete(user_id)
        if user is None:
            raise UserNotFound(user_id)

        # TODO: Replace hard deletion with soft deletion or anonymization
        # where reviews and places must retain a valid user reference.
        return user

    def create_amenity(self, amenity_data, is_admin):
        if not is_admin:
            raise AdminPrivilegesRequired()

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

    def update_amenity(self, amenity_id, amenity_data, is_admin):
        if not is_admin:
            raise AdminPrivilegesRequired()

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
            title=data["title"],
            description=data.get("description", ""),
            price=data["price"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            owner=owner,
            amenities=amenities,
        )
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

    def update_place(
        self,
        place_id,
        place_data,
        current_user_id,
        is_admin,
    ):
        place = self.place_repo.get(place_id)
        if place is None:
            raise PlaceNotFound(place_id)

        # JWT at the API layer only extracts the user identity.
        if not is_admin and (
            current_user_id is None or place.owner_id != current_user_id
        ):
            raise UnauthorizedAction()

        validate_allowed_fields(
            place_data,
            ALLOWED_PLACE_UPDATE_FIELDS,
            resource_name="place",
        )

        data = place_data.copy()

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

    def create_review(self, review_data, is_admin=False):
        data = review_data.copy()
        place = self.place_repo.get(data["place_id"])
        if place is None:
            raise PlaceNotFound(data["place_id"])

        user = self.user_repo.get(data["user_id"])
        if user is None:
            raise UserNotFound(data["user_id"])

        if not is_admin and user.id == place.owner_id:
            raise OwnerCannotReviewOwnPlace()

        if not is_admin and self.review_repo.find_one(
            place_id=place.id,
            user_id=user.id,
        ):
            raise DuplicateReview()

        data.pop("place_id")
        data.pop("user_id")
        review = Review(place=place, user=user, **data)
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

        return self.review_repo.find_all(place_id=place.id)

    def get_reviews_by_user(self, user_id):
        user = self.user_repo.get(user_id)
        if user is None:
            raise UserNotFound(user_id)

        return self.review_repo.find_all(user_id=user.id)

    def update_review(
        self,
        review_id,
        review_data,
        current_user_id,
        is_admin,
    ):
        data = review_data.copy()

        review = self.review_repo.get(review_id)
        if review is None:
            raise ReviewNotFound(review_id)

        if not is_admin and review.user_id != current_user_id:
            raise UnauthorizedAction()

        validate_allowed_fields(
            data,
            ALLOWED_REVIEW_UPDATE_FIELDS,
            resource_name="review",
        )

        updated_review = self.review_repo.update(review_id, data)
        if updated_review is None:
            raise ReviewNotFound(review_id)

        return updated_review

    def delete_review(
        self,
        review_id,
        current_user_id,
        is_admin,
    ):
        review = self.review_repo.get(review_id)
        if review is None:
            raise ReviewNotFound(review_id)

        if not is_admin and review.user_id != current_user_id:
            raise UnauthorizedAction()

        self.review_repo.delete(review_id)
        return review
