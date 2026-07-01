from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource
from api.v1.schemas.review import (
    reviewRequestModel,
    reviewResponseModel,
    reviewUpdateModel,
)
from services import facade

api = Namespace("reviews", description="Review operations")
review_model = api.model("Review", reviewRequestModel)
review_update_model = api.model("ReviewUpdate", reviewUpdateModel)
review_response_model = api.model("ReviewResponse", reviewResponseModel)


@api.route("/")
class ReviewList(Resource):
    @api.marshal_list_with(review_response_model)
    @api.response(200, "Reviews retrieved successfully")
    def get(self):
        """List all reviews"""
        return facade.get_all_reviews(), 200

    @api.marshal_with(review_response_model)
    @api.expect(review_model, validate=True)
    @api.response(201, "Review successfully created")
    @api.response(400, "Invalid input data")
    @api.response(401, "Missing or invalid JWT")
    @api.response(404, "User or place not found")
    @jwt_required()
    def post(self):
        """Create a new review"""
        review_data = api.payload.copy()
        review_data["user_id"] = get_jwt_identity()
        review = facade.create_review(review_data)
        return review, 201


@api.route("/<review_id>")
class ReviewResource(Resource):
    @api.marshal_with(review_response_model)
    @api.response(200, "Review details retrieved successfully")
    @api.response(404, "Review not found")
    def get(self, review_id):
        """Get review details by ID"""
        review = facade.get_review(review_id)
        return review, 200

    @api.expect(review_update_model, validate=True)
    @api.response(200, "Review successfully updated")
    @api.response(400, "Invalid input data")
    @api.response(401, "Missing or invalid JWT")
    @api.response(403, "Unauthorized action")
    @api.response(404, "Review not found")
    @jwt_required()
    def put(self, review_id):
        """Update review details by ID"""
        current_user_id = get_jwt_identity()
        facade.update_review(
            review_id,
            api.payload,
            current_user_id=current_user_id,
        )
        return {"message": "Review updated successfully"}, 200

    @api.response(200, "Review successfully deleted")
    @api.response(401, "Missing or invalid JWT")
    @api.response(403, "Unauthorized action")
    @api.response(404, "Review not found")
    @jwt_required()
    def delete(self, review_id):
        """Delete review by ID"""
        current_user_id = get_jwt_identity()
        facade.delete_review(
            review_id,
            current_user_id=current_user_id,
        )
        return {"message": "Review deleted successfully"}, 200
