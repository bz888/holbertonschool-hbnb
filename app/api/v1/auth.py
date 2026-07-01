from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from flask_restx import Namespace, Resource

from api.v1.schemas.auth import (
    loginModel,
    jwtErrorModel,
    loginResponseModel,
    protectedResponseModel,
)
from services import facade


api = Namespace("auth", description="Authentication operations")

login_model = api.model("Login", loginModel)
login_response_model = api.model(
    "LoginResponse",
    loginResponseModel,
)
protected_response_model = api.model(
    "ProtectedResponse",
    protectedResponseModel,
)
jwt_error_model = api.model(
    "JwtError",
    jwtErrorModel,
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


@api.route("/protected")
class ProtectedResource(Resource):
    @api.response(
        200,
        "Protected route accessed successfully",
        protected_response_model,
    )
    @api.response(401, "Missing or invalid JWT", jwt_error_model)
    @api.response(422, "Invalid JWT payload", jwt_error_model)
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        claims = get_jwt()
        return {
            "message": f"Hello, user {current_user}",
            "is_admin": claims["is_admin"],
        }, 200
