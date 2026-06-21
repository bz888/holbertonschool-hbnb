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

place_owner_response_model = api.model('PlaceOwnerResponse', {
    'id': fields.String(description='ID of the owner'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

place_amenity_response_model = api.model('PlaceAmenityResponse', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

place_review_response_model = api.model('PlaceReviewResponse', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Review text'),
    'rating': fields.Integer(description='Rating from 1 to 5'),
    'place_id': fields.String(
        attribute=lambda review: review.place.id,
        description='ID of the reviewed place'
    ),
    'user_id': fields.String(
        attribute=lambda review: review.user.id,
        description='ID of the review author'
    )
})

place_response_model = api.model('PlaceResponse', {
    'id': fields.String(description='Place ID'),
    'title': fields.String(description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(description='Price per night'),
    'latitude': fields.Float(description='Latitude of the place'),
    'longitude': fields.Float(description='Longitude of the place'),
    'owner_id': fields.String(
        attribute=lambda place: place.owner.id,
        description='ID of the owner'
    ),
    'owner': fields.Nested(
        place_owner_response_model,
        description='Owner details'
    ),
    'amenities': fields.List(
        fields.Nested(place_amenity_response_model),
        description='Amenities associated with the place'
    ),
    'reviews': fields.List(
        fields.Nested(place_review_response_model),
        description='Reviews associated with the place'
    )
})

review_for_place_model = api.model('PlaceReview', {
    'text': fields.String(required=True, description='Review text'),
    'rating': fields.Integer(required=True, description='Rating from 1 to 5'),
    'user_id': fields.String(required=True, description='ID of the user')
})


@api.route('/')
class PlaceList(Resource):
    @api.marshal_list_with(place_response_model)
    @api.response(200, 'Places retrieved successfully')
    def get(self):
        """List all places"""
        return facade.get_all_places(), 200

    @api.marshal_with(place_response_model)
    @api.expect(place_model, validate=True)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Create a new place"""
        place = facade.create_place(api.payload)
        return place, 201


@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.marshal_with(place_response_model)
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details by ID"""
        place = facade.get_place(place_id)
        return place, 200

    @api.expect(place_update_model, validate=True)
    @api.response(200, 'Place successfully updated')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'Place not found')
    def put(self, place_id):
        """Update place details by ID"""
        facade.update_place(place_id, api.payload)
        return {'message': 'Place updated successfully'}, 200

    @api.response(200, 'Place successfully deleted')
    @api.response(404, 'Place not found')
    def delete(self, place_id):
        """Delete place by ID"""
        facade.delete_place(place_id)
        return {'message': 'Place deleted successfully'}, 200

@api.route('/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.marshal_list_with(place_review_response_model)
    @api.response(200, 'Reviews retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """List all reviews for a place"""
        return facade.get_reviews_by_place(place_id), 200

    @api.marshal_with(place_review_response_model)
    @api.expect(review_for_place_model, validate=True)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'Place not found')
    def post(self, place_id):
        """Create a review for a place"""
        review_data = api.payload.copy()
        review_data['place_id'] = place_id

        review = facade.create_review(review_data)
        return review, 201
