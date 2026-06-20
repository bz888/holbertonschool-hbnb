class PlaceNotFound(Exception):
    """Raised when a place cannot be found."""

    def __init__(self, place_id):
        super().__init__(f"Place '{place_id}' not found")
