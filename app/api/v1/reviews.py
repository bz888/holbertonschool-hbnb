from flask_restx import Namespace, Resource, fields
from services import facade

api = Namespace('reviews', description='Review operations')
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Review text'),
    'rating': fields.Integer(required=True, description='Rating from 1 to 5'),
    'place_id': fields.String(required=True, description='ID of the place'),
    'user_id': fields.String(required=True, description='ID of the user')
})

review_update_model = api.model('ReviewUpdate', {
    'text': fields.String(required=False, description='Review text'),
    'rating': fields.Integer(required=False, description='Rating from 1 to 5'),
    'place_id': fields.String(required=False, description='ID of the place'),
    'user_id': fields.String(required=False, description='ID of the user')
})


@api.route('/')
class ReviewList(Resource):
    @api.response(200, 'Reviews retrieved successfully')
    def get(self):
        """List all reviews"""
        return [review.to_dict() for review in facade.get_all_reviews()], 200

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID"""
        review = facade.get_review(review_id)
        return review.to_dict(), 200

    @api.expect(review_update_model, validate=True)
    @api.response(200, 'Review successfully updated')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'Review not found')
    def put(self, review_id):
        """Update review details by ID"""
        review = facade.update_review(review_id, api.payload)
        return review.to_dict(), 200

    @api.response(200, 'Review successfully deleted')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete review by ID"""
        facade.delete_review(review_id)
        return {'message': 'Review deleted successfully'}, 200
