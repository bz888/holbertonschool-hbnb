from flask_restx import Namespace, Resource, fields
from services import facade
from utils.error import EmailAlreadyRegistered, UserNotFound


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


@api.route("/")
class UserList(Resource):
    """Handle operations on the user collection."""

    @api.response(200, "Users retrieved successfully")
    def get(self):
        """List all users."""
        return [
            user.to_dict() for user in facade.get_all_users()
        ], 200

    @api.expect(user_model, validate=True)
    @api.response(201, "User successfully created")
    @api.response(400, "Invalid input data")
    @api.response(409, "Email already registered")
    def post(self):
        """Register a new user."""
        try:
            new_user = facade.create_user(api.payload)
            return new_user.to_dict(), 201
        except EmailAlreadyRegistered:
            return {"error": "Email already registered"}, 409
        except ValueError as exc:
            return {"error": str(exc)}, 400


@api.route("/<user_id>")
class UserResource(Resource):
    """Handle operations on an individual user."""

    @api.response(200, "User details retrieved successfully")
    @api.response(404, "User not found")
    def get(self, user_id):
        """Get user details by ID."""
        try:
            user = facade.get_user(user_id)
            return user.to_dict(), 200
        except UserNotFound:
            return {"error": "User not found"}, 404

    @api.expect(user_update_model, validate=True)
    @api.response(200, "User successfully updated")
    @api.response(400, "Invalid input data")
    @api.response(404, "User not found")
    @api.response(409, "Email already registered")
    def put(self, user_id):
        """Update user details by ID."""
        try:
            user = facade.update_user(user_id, api.payload)
            return user.to_dict(), 200
        except UserNotFound:
            return {"error": "User not found"}, 404
        except EmailAlreadyRegistered:
            return {"error": "Email already registered"}, 409
        except ValueError as exc:
            return {"error": str(exc)}, 400

    @api.response(200, "User successfully deleted")
    @api.response(404, "User not found")
    def delete(self, user_id):
        """Delete user by ID."""
        try:
            facade.delete_user(user_id)
            return {"message": "User deleted successfully"}, 200
        except UserNotFound:
            return {"error": "User not found"}, 404
