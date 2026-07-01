from flask_restx import fields

reviewRequestModel = {
    "text": fields.String(required=True, description="Review text"),
    "rating": fields.Integer(
        required=True,
        description="Rating from 1 to 5",
    ),
    "place_id": fields.String(
        required=True,
        description="ID of the place",
    ),
    "user_id": fields.String(required=True, description="ID of the user"),
}

reviewUpdateModel = {
    "text": fields.String(required=False, description="Review text"),
    "rating": fields.Integer(
        required=False,
        description="Rating from 1 to 5",
    ),
}

reviewResponseModel = {
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
