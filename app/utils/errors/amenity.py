class AmenityNotFound(Exception):
    """Raised when an amenity cannot be found."""

    def __init__(self, amenity_id):
        super().__init__(f"Amenity '{amenity_id}' not found")