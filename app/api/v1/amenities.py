from flask_restx import Namespace, Resource
from api.v1.schemas.amenity import (
    amenityRequestModel,
    amenityResponseModel,
    amenityUpdateModel,
)
from services import facade

api = Namespace('amenities', description='Amenity operations')

amenity_model = api.model('Amenity', amenityRequestModel)
amenity_update_model = api.model('AmenityUpdate', amenityUpdateModel)
amenity_response_model = api.model('AmenityResponse', amenityResponseModel)


@api.route('/')
class AmenityList(Resource):
    @api.marshal_list_with(amenity_response_model)
    @api.response(200, 'Amenities retrieved successfully')
    def get(self):
        """List all amenities"""
        return facade.get_all_amenities(), 200

    @api.marshal_with(amenity_response_model)
    @api.expect(amenity_model, validate=True)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Create a new amenity"""
        amenity = facade.create_amenity(api.payload)
        return amenity, 201


@api.route('/<amenity_id>')
class AmenityResource(Resource):
    @api.marshal_with(amenity_response_model)
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get amenity details by ID"""
        amenity = facade.get_amenity(amenity_id)
        return amenity, 200

    @api.expect(amenity_update_model, validate=True)
    @api.response(200, 'Amenity successfully updated')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'Amenity not found')
    def put(self, amenity_id):
        """Update an existing amenity"""
        facade.update_amenity(amenity_id, api.payload)
        return {'message': 'Amenity updated successfully'}, 200

    @api.response(200, 'Amenity successfully deleted')
    @api.response(404, 'Amenity not found')
    def delete(self, amenity_id):
        """Delete amenity by ID"""
        facade.delete_amenity(amenity_id)
        return {'message': 'Amenity deleted successfully'}, 200
