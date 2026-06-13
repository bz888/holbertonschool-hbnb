from flask_restx import Namespace, Resource, fields
from services import facade

api = Namespace('amenities', description='Amenity operations')

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

amenity_update_model = api.model('AmenityUpdate', {
    'name': fields.String(required=False, description='Name of the amenity')
})


@api.route('/')
class AmenityList(Resource):
    @api.response(200, 'Amenities retrieved successfully')
    def get(self):
        """List all amenities"""
        return [amenity.to_dict() for amenity in facade.get_all_amenities()], 200

    @api.expect(amenity_model, validate=True)
    @api.response(201, 'Amenity successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Create a new amenity"""
        amenity = facade.create_amenity(api.payload)
        return amenity.to_dict(), 201


@api.route('/<amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details retrieved successfully')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get amenity details by ID"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return amenity.to_dict(), 200

    @api.expect(amenity_update_model, validate=True)
    @api.response(200, 'Amenity successfully updated')
    @api.response(404, 'Amenity not found')
    def put(self, amenity_id):
        """Update amenity details by ID"""
        amenity = facade.update_amenity(amenity_id, api.payload)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return amenity.to_dict(), 200

    @api.response(200, 'Amenity successfully deleted')
    @api.response(404, 'Amenity not found')
    def delete(self, amenity_id):
        """Delete amenity by ID"""
        amenity = facade.delete_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return {'message': 'Amenity deleted successfully'}, 200
