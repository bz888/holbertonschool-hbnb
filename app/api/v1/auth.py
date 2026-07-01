from flask_jwt_extended import create_access_token, jwt_required
from flask_restx import Namespace, Resource, fields

from api.v1.schemas.auth import (
    loginModel,
    loginResponseModel
)
from services import facade


api = Namespace("auth", description="Authentication operations")

login_model = api.model("Login", loginModel)
login_response_model = api.model(
    "LoginResponse",
    loginResponseModel
)

@api.route("/login")
class Login(Resource):
    @api.expect(login_model, validate=True)
    @api.response(200, "Login successful", login_response_model)
    @api.response(401, "Invalid credentials")
    def post(self):
        """Authenticate user and return a JWT token"""
        credentials = api.payload

        user = facade.get_user_by_email(credentials["email"])

        if not user or not user.verify_password(credentials["password"]):
            return {"error": "Invalid credentials"}, 401

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"is_admin": user.is_admin},
        )

        return {"access_token": access_token}, 200
