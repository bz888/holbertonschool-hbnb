from flask_restx import Namespace, Resource, fields
from services import facade


api = Namespace("users", description="User operations")

user_model = api.model(
    "User",
    {
        "first_name": fields.String(
            required=True,
            description="First name of the user",
        ),
        "last_name": fields.String(
            required=True,
            description="Last name of the user",
        ),
        "email": fields.String(
            required=True,
            description="Email of the user",
        ),
    },
)

user_update_model = api.model(
    "UserUpdate",
    {
        "first_name": fields.String(
            required=False,
            description="First name of the user",
        ),
        "last_name": fields.String(
            required=False,
            description="Last name of the user",
        ),
        "email": fields.String(
            required=False,
            description="Email of the user",
        ),
    },
)

user_response_model = api.model(
    "UserResponse",
    {
        "id": fields.String(description="ID of the user"),
        "first_name": fields.String(
            description="First name of the user",
        ),
        "last_name": fields.String(
            description="Last name of the user",
        ),
        "email": fields.String(
            description="Email of the user",
        ),
    },
)

user_review_response_model = api.model(
    "UserReviewResponse",
    {
        "id": fields.String(description="ID of the review"),
        "text": fields.String(description="Review text"),
        "rating": fields.Integer(description="Rating from 1 to 5"),
        "place_id": fields.String(
            attribute=lambda review: review.place.id,
            description="ID of the reviewed place",
        ),
        "user_id": fields.String(
            attribute=lambda review: review.user.id,
            description="ID of the review author",
        ),
    },
)


@api.route("/")
class UserList(Resource):
    """Handle operations on the user collection."""

    @api.marshal_list_with(user_response_model)
    @api.response(200, "Users retrieved successfully")
    def get(self):
        """List all users."""
        return facade.get_all_users(), 200

    @api.marshal_with(user_response_model)
    @api.expect(user_model, validate=True)
    @api.response(201, "User successfully created")
    @api.response(400, "Invalid input data")
    @api.response(400, "Email already registered")
    def post(self):
        """Register a new user."""
        new_user = facade.create_user(api.payload)
        return new_user, 201


@api.route("/<user_id>")
class UserResource(Resource):
    """Handle operations on an individual user."""

    @api.marshal_with(user_response_model)
    @api.response(200, "User details retrieved successfully")
    @api.response(404, "User not found")
    def get(self, user_id):
        """Get user details by ID."""
        user = facade.get_user(user_id)
        return user, 200

    @api.marshal_with(user_response_model)
    @api.expect(user_update_model, validate=True)
    @api.response(200, "User successfully updated")
    @api.response(400, "Invalid input data")
    @api.response(404, "User not found")
    @api.response(400, "Email already registered")
    def put(self, user_id):
        """Update user details by ID."""
        user = facade.update_user(user_id, api.payload)
        return user, 200

    @api.response(200, "User permanently deleted")
    @api.response(404, "User not found")
    def delete(self, user_id):
        """Permanently delete user by ID."""
        facade.delete_user(user_id)
        return {"message": "User permanently deleted"}, 200


@api.route("/<user_id>/soft-delete")
class UserSoftDeleteResource(Resource):
    """Handle soft deletion of a user."""

    @api.response(200, "User successfully deactivated")
    @api.response(404, "User not found")
    def delete(self, user_id):
        """Deactivate a user and their places."""
        facade.soft_delete_user(user_id)
        return {"message": "User deactivated successfully"}, 200


@api.route("/<user_id>/reviews")
class UserReviewList(Resource):
    """Handle review listing for a user."""

    @api.marshal_list_with(user_review_response_model)
    @api.response(200, "Reviews retrieved successfully")
    @api.response(404, "User not found")
    def get(self, user_id):
        """List reviews written by a user."""
        return facade.get_reviews_by_user(user_id), 200
