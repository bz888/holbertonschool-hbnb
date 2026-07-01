 
from flask_restx import fields
 
 
loginModel =  {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
}

loginResponseModel = {
        "access_token": fields.String(
            required=True,
            description="JWT access token",
        )
    }