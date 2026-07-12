from models.amenity import Amenity
from persistence.repository import SQLAlchemyRepository


class AmenityRepository(SQLAlchemyRepository):

    def __init__(self):
        super().__init__(Amenity)