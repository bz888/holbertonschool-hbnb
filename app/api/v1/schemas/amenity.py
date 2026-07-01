from flask_restx import fields

amenityRequestModel = {
    "name": fields.String(
        required=True,
        description="Name of the amenity",
    ),
}

amenityUpdateModel = {
    "name": fields.String(
        required=False,
        description="Name of the amenity",
    ),
}

amenityResponseModel = {
    "id": fields.String(description="ID of the amenity"),
    "name": fields.String(description="Name of the amenity"),
}
