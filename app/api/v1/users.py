from flask_restx import Namespace, Resource, fields
from services import facade

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user')
})

user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(required=False, description='First name of the user'),
    'last_name': fields.String(required=False, description='Last name of the user'),
    'email': fields.String(required=False, description='Email of the user')
})


@api.route('/')
class UserList(Resource):
    @api.response(200, 'Users retrieved successfully')
    def get(self):
        """List all users"""
        return [user.to_dict() for user in facade.get_all_users()], 200

    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new user"""
        user_data = api.payload

        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            return {'error': 'Email already registered'}, 400

        try:
            new_user = facade.create_user(user_data)
        except ValueError as exc:
            return {'error': str(exc)}, 400

        return new_user.to_dict(), 201


@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict(), 200

    @api.expect(user_update_model, validate=True)
    @api.response(200, 'User successfully updated')
    @api.response(400, 'Email already registered')
    @api.response(404, 'User not found')
    def put(self, user_id):
        """Update user details by ID"""
        if not facade.get_user(user_id):
            return {'error': 'User not found'}, 404

        try:
            user = facade.update_user(user_id, api.payload)
            if not user:
                return {'error': 'User not found'}, 404
        except ValueError as exc:
            return {'error': str(exc)}, 400

        return user.to_dict(), 200

    @api.response(200, 'User successfully deleted')
    @api.response(404, 'User not found')
    def delete(self, user_id):
        """Delete user by ID"""
        user = facade.delete_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return {'message': 'User deleted successfully'}, 200
