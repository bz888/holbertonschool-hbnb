from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, fields
from api.v1.schemas.place import (
    placeAmenityResponseModel,
    placeOwnerResponseModel,
    placeRequestModel,
    placeResponseModel,
    placeReviewRequestModel,
    placeReviewResponseModel,
    placeUpdateModel,
)
from services import facade

api = Namespace("places", description="Place operations")

place_model = api.model("Place", placeRequestModel)
place_update_model = api.model("PlaceUpdate", placeUpdateModel)
place_owner_response_model = api.model(
    "PlaceOwnerResponse",
    placeOwnerResponseModel,
)
place_amenity_response_model = api.model(
    "PlaceAmenityResponse",
    placeAmenityResponseModel,
)
place_review_response_model = api.model(
    "PlaceReviewResponse",
    placeReviewResponseModel,
)
place_response_schema = {
    **placeResponseModel,
    "owner": fields.Nested(
        place_owner_response_model,
        description="Owner details",
    ),
    "amenities": fields.List(
        fields.Nested(place_amenity_response_model),
        description="Amenities associated with the place",
    ),
    "reviews": fields.List(
        fields.Nested(place_review_response_model),
        description="Reviews associated with the place",
    ),
}
place_response_model = api.model("PlaceResponse", place_response_schema)
review_for_place_model = api.model("PlaceReview", placeReviewRequestModel)


@api.route("/")
class PlaceList(Resource):
    @api.marshal_list_with(place_response_model)
    @api.response(200, "Places retrieved successfully")
    def get(self):
        """List all places"""
        return facade.get_all_places(), 200

    @api.marshal_with(place_response_model)
    @api.expect(place_model, validate=True)
    @api.response(201, "Place successfully created")
    @api.response(400, "Invalid input data")
    @api.response(401, "Missing or invalid JWT")
    @api.response(404, "User not found")
    @jwt_required()
    def post(self):
        """Create a new place"""
        place_data = api.payload.copy()
        place_data["owner_id"] = get_jwt_identity()
        place = facade.create_place(place_data)
        return place, 201


@api.route("/<place_id>")
class PlaceResource(Resource):
    @api.marshal_with(place_response_model)
    @api.response(200, "Place details retrieved successfully")
    @api.response(404, "Place not found")
    def get(self, place_id):
        """Get place details by ID"""
        place = facade.get_place(place_id)
        return place, 200

    @api.expect(place_update_model, validate=True)
    @api.response(200, "Place successfully updated")
    @api.response(400, "Invalid input data")
    @api.response(401, "Missing or invalid JWT")
    @api.response(403, "Unauthorized action")
    @api.response(404, "Place not found")
    @jwt_required()
    def put(self, place_id):
        """Update place details by ID"""
        current_user_id = get_jwt_identity()
        facade.update_place(
            place_id,
            api.payload,
            current_user_id,
            is_admin=get_jwt().get("is_admin", False) is True,
        )
        return {"message": "Place updated successfully"}, 200

    @api.response(200, "Place successfully deleted")
    @api.response(404, "Place not found")
    def delete(self, place_id):
        """Delete place by ID"""
        facade.delete_place(place_id)
        return {"message": "Place deleted successfully"}, 200


@api.route("/<place_id>/reviews")
class PlaceReviewList(Resource):
    @api.marshal_list_with(place_review_response_model)
    @api.response(200, "Reviews retrieved successfully")
    @api.response(404, "Place not found")
    def get(self, place_id):
        """List all reviews for a place"""
        return facade.get_reviews_by_place(place_id), 200

    @api.marshal_with(place_review_response_model)
    @api.expect(review_for_place_model, validate=True)
    @api.response(201, "Review successfully created")
    @api.response(400, "Invalid input data")
    @api.response(401, "Missing or invalid JWT")
    @api.response(404, "Place not found")
    @jwt_required()
    def post(self, place_id):
        """Create a review for a place"""
        review_data = api.payload.copy()
        review_data["place_id"] = place_id
        review_data["user_id"] = get_jwt_identity()

        review = facade.create_review(review_data)
        return review, 201
