from abc import ABC, abstractmethod

from sqlalchemy import select

from extensions import db


class Repository(ABC):
    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def get(self, obj_id):
        pass

    @abstractmethod
    def get_all(self) -> list:
        pass

    @abstractmethod
    def find_one(self, **filters):
        pass

    @abstractmethod
    def find_all(self, **filters) -> list:
        pass

    @abstractmethod
    def update(self, obj_id, data):
        pass

    @abstractmethod
    def delete(self, obj_id):
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        pass


class SQLAlchemyRepository(Repository):
    """Generic repository backed by the active SQLAlchemy session."""

    def __init__(self, model):
        self.model = model

    def add(self, obj):
        try:
            db.session.add(obj)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return obj

    def get(self, obj_id):
        return db.session.get(self.model, obj_id)

    def get_all(self):
        return list(db.session.scalars(select(self.model)).all())

    def find_one(self, **filters):
        statement = select(self.model).filter_by(**filters).limit(1)
        return db.session.scalar(statement)

    def find_all(self, **filters):
        statement = select(self.model).filter_by(**filters)
        return list(db.session.scalars(statement).all())

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if obj is None:
            return None

        try:
            for key, value in data.items():
                setattr(obj, key, value)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return obj

    def delete(self, obj_id):
        obj = self.get(obj_id)
        if obj is None:
            return None

        try:
            db.session.delete(obj)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return obj

    def get_by_attribute(self, attr_name, attr_value):
        return self.find_one(**{attr_name: attr_value})

    def clear(self):
        """Delete all model rows while honoring ORM relationship cascades."""
        try:
            for obj in self.get_all():
                db.session.delete(obj)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
