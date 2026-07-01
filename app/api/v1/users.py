from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource
from api.v1.schemas.user import (
    userCreatedResponseModel,
    userRequestModel,
    userResponseModel,
    userReviewResponseModel,
    userUpdateModel,
)
from services import facade

api = Namespace("users", description="User operations")

user_model = api.model("User", userRequestModel)
user_update_model = api.model("UserUpdate", userUpdateModel)
user_response_model = api.model("UserResponse", userResponseModel)
user_created_response_model = api.model(
    "UserCreatedResponse",
    userCreatedResponseModel,
)
user_review_response_model = api.model(
    "UserReviewResponse",
    userReviewResponseModel,
)


@api.route("/")
class UserList(Resource):
    """Handle operations on the user collection."""

    @api.marshal_list_with(user_response_model)
    @api.response(200, "Users retrieved successfully")
    def get(self):
        """List all users."""
        return facade.get_all_users(), 200

    @api.marshal_with(user_created_response_model)
    @api.expect(user_model, validate=True)
    @api.response(201, "User successfully created")
    @api.response(400, "Invalid input data")
    @api.response(400, "Email already registered")
    def post(self):
        """Register a new user."""
        new_user = facade.create_user(api.payload)
        return {
            "id": new_user.id,
            "message": "User successfully created",
        }, 201


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
    @api.response(401, "Missing or invalid JWT")
    @api.response(403, "Unauthorized action")
    @api.response(404, "User not found")
    @jwt_required()
    def put(self, user_id):
        """Update user details by ID."""
        current_user_id = get_jwt_identity()
        user = facade.update_user(
            user_id,
            api.payload,
            current_user_id=current_user_id,
        )
        return user, 200

    @api.response(200, "User permanently deleted")
    @api.response(404, "User not found")
    def delete(self, user_id):
        """Permanently delete user by ID."""
        facade.delete_user(user_id)
        return {"message": "User permanently deleted"}, 200


# future implementation for soft deletion, purpose for addressing loose review relationships
# @api.route("/<user_id>/soft-delete")
# class UserSoftDeleteResource(Resource):
#     """Handle soft deletion of a user."""

#     @api.response(200, "User successfully deactivated")
#     @api.response(404, "User not found")
#     def delete(self, user_id):
#         """Deactivate a user and their places."""
#         facade.soft_delete_user(user_id)
#         return {"message": "User deactivated successfully"}, 200


@api.route("/<user_id>/reviews")
class UserReviewList(Resource):
    """Handle review listing for a user."""

    @api.marshal_list_with(user_review_response_model)
    @api.response(200, "Reviews retrieved successfully")
    @api.response(404, "User not found")
    def get(self, user_id):
        """List reviews written by a user."""
        return facade.get_reviews_by_user(user_id), 200
