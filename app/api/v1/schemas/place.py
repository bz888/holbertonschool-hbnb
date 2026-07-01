from flask_restx import fields

placeRequestModel = {
    "title": fields.String(
        required=True,
        description="Title of the place",
    ),
    "description": fields.String(
        required=False,
        description="Description of the place",
    ),
    "price": fields.Float(required=True, description="Price per night"),
    "latitude": fields.Float(
        required=True,
        description="Latitude of the place",
    ),
    "longitude": fields.Float(
        required=True,
        description="Longitude of the place",
    ),
    "owner_id": fields.String(
        required=True,
        description="ID of the owner",
    ),
    "amenity_ids": fields.List(
        fields.String,
        required=False,
        description="Amenity IDs",
    ),
}

placeUpdateModel = {
    "title": fields.String(
        required=False,
        description="Title of the place",
    ),
    "description": fields.String(
        required=False,
        description="Description of the place",
    ),
    "price": fields.Float(required=False, description="Price per night"),
    "latitude": fields.Float(
        required=False,
        description="Latitude of the place",
    ),
    "longitude": fields.Float(
        required=False,
        description="Longitude of the place",
    ),
    "owner_id": fields.String(
        required=False,
        description="ID of the owner",
    ),
    "amenity_ids": fields.List(
        fields.String,
        required=False,
        description="Amenity IDs",
    ),
}

placeOwnerResponseModel = {
    "id": fields.String(description="ID of the owner"),
    "first_name": fields.String(description="First name of the owner"),
    "last_name": fields.String(description="Last name of the owner"),
    "email": fields.String(description="Email of the owner"),
}

placeAmenityResponseModel = {
    "id": fields.String(description="Amenity ID"),
    "name": fields.String(description="Name of the amenity"),
}

placeReviewResponseModel = {
    "id": fields.String(description="Review ID"),
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

placeResponseModel = {
    "id": fields.String(description="Place ID"),
    "title": fields.String(description="Title of the place"),
    "description": fields.String(description="Description of the place"),
    "price": fields.Float(description="Price per night"),
    "latitude": fields.Float(description="Latitude of the place"),
    "longitude": fields.Float(description="Longitude of the place"),
    "owner_id": fields.String(
        attribute=lambda place: place.owner.id,
        description="ID of the owner",
    ),
}

placeReviewRequestModel = {
    "text": fields.String(required=True, description="Review text"),
    "rating": fields.Integer(
        required=True,
        description="Rating from 1 to 5",
    ),
    "user_id": fields.String(required=True, description="ID of the user"),
}
