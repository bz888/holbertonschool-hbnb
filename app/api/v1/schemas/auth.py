from flask_restx import fields


loginModel = {
    "email": fields.String(required=True, description="User email"),
    "password": fields.String(required=True, description="User password"),
}

loginResponseModel = {
    "access_token": fields.String(
        required=True,
        description="JWT access token",
    )
}

protectedResponseModel = {
    "message": fields.String(
        required=True,
        description="Message containing the current user identity",
    ),
    "is_admin": fields.Boolean(
        required=True,
        description="Admin status from the JWT additional claims",
    ),
}

jwtErrorModel = {
    "msg": fields.String(
        required=True,
        description="JWT error message",
    ),
}
