from flask_restx import fields

userRequestModel = {
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
    "password": fields.String(
        required=True,
        description="Password of the user",
    ),
}

userUpdateModel = {
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
}

userResponseModel = {
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
}

userCreatedResponseModel = {
    "id": fields.String(description="ID of the user"),
    "message": fields.String(description="Success message"),
}

userReviewResponseModel = {
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
}
