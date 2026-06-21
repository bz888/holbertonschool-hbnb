from flask_restx import Namespace, Resource, fields
from services import facade

api = Namespace("reviews", description="Review operations")
review_model = api.model(
    "Review",
    {
        "text": fields.String(required=True, description="Review text"),
        "rating": fields.Integer(
            required=True, description="Rating from 1 to 5"
        ),
        "place_id": fields.String(
            required=True, description="ID of the place"
        ),
        "user_id": fields.String(required=True, description="ID of the user"),
    },
)

review_update_model = api.model(
    "ReviewUpdate",
    {
        "text": fields.String(required=False, description="Review text"),
        "rating": fields.Integer(
            required=False, description="Rating from 1 to 5"
        ),
    },
)

review_response_model = api.model(
    "ReviewResponse",
    {
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
    },
)


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
    @api.response(404, "User or place not found")
    def post(self):
        """Create a new review"""
        review = facade.create_review(api.payload)
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
    @api.response(404, "Review not found")
    def put(self, review_id):
        """Update review details by ID"""
        facade.update_review(review_id, api.payload)
        return {"message": "Review updated successfully"}, 200

    @api.response(200, "Review successfully deleted")
    @api.response(404, "Review not found")
    def delete(self, review_id):
        """Delete review by ID"""
        facade.delete_review(review_id)
        return {"message": "Review deleted successfully"}, 200
