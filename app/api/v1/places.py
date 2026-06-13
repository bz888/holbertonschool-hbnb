from flask_restx import Namespace, Resource, fields
from services import facade

api = Namespace('places', description='Place operations')

place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(required=False, description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'amenity_ids': fields.List(fields.String, required=False, description='Amenity IDs')
})

place_update_model = api.model('PlaceUpdate', {
    'title': fields.String(required=False, description='Title of the place'),
    'description': fields.String(required=False, description='Description of the place'),
    'price': fields.Float(required=False, description='Price per night'),
    'latitude': fields.Float(required=False, description='Latitude of the place'),
    'longitude': fields.Float(required=False, description='Longitude of the place'),
    'owner_id': fields.String(required=False, description='ID of the owner'),
    'amenity_ids': fields.List(fields.String, required=False, description='Amenity IDs')
})

review_for_place_model = api.model('PlaceReview', {
    'text': fields.String(required=True, description='Review text'),
    'rating': fields.Integer(required=True, description='Rating from 1 to 5'),
    'user_id': fields.String(required=True, description='ID of the user')
})


@api.route('/')
class PlaceList(Resource):
    @api.response(200, 'Places retrieved successfully')
    def get(self):
        """List all places"""
        return [place.to_dict() for place in facade.get_all_places()], 200

    @api.expect(place_model, validate=True)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Create a new place"""
        try:
            place = facade.create_place(api.payload)
        except ValueError as exc:
            return {'error': str(exc)}, 400
        return place.to_dict(), 201


@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details by ID"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        return place.to_dict(), 200

    @api.expect(place_update_model, validate=True)
    @api.response(200, 'Place successfully updated')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'Place not found')
    def put(self, place_id):
        """Update place details by ID"""
        if not facade.get_place(place_id):
            return {'error': 'Place not found'}, 404

        try:
            place = facade.update_place(place_id, api.payload)
        except ValueError as exc:
            return {'error': str(exc)}, 400
        if not place:
            return {'error': 'Place not found'}, 404

        return place.to_dict(), 200

    @api.response(200, 'Place successfully deleted')
    @api.response(404, 'Place not found')
    def delete(self, place_id):
        """Delete place by ID"""
        place = facade.delete_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        return {'message': 'Place deleted successfully'}, 200


@api.route('/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'Reviews retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """List all reviews for a place"""
        if not facade.get_place(place_id):
            return {'error': 'Place not found'}, 404
        reviews = facade.get_reviews_by_place(place_id)
        return [review.to_dict() for review in reviews], 200

    @api.expect(review_for_place_model, validate=True)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'Place not found')
    def post(self, place_id):
        """Create a review for a place"""
        if not facade.get_place(place_id):
            return {'error': 'Place not found'}, 404

        review_data = api.payload.copy()
        review_data['place_id'] = place_id

        try:
            review = facade.create_review(review_data)
        except ValueError as exc:
            return {'error': str(exc)}, 400

        return review.to_dict(), 201
