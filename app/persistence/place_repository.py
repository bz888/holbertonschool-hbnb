from models.place import Place
from persistence.repository import SQLAlchemyRepository


class PlaceRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Place)
