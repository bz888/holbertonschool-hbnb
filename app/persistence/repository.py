from abc import ABC, abstractmethod


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


class InMemoryRepository(Repository):
    """Simple in-memory persistence repository."""

    def __init__(self):
        self._storage = {}

    def add(self, obj):
        self._storage[obj.id] = obj
        return obj

    def get(self, obj_id):
        return self._storage.get(obj_id)

    def get_all(self):
        return list(self._storage.values())

    def find_one(self, **filters):
        """Return the first object matching every supplied filter."""
        return next(
            (
                obj
                for obj in self._storage.values()
                if self._matches(obj, filters)
            ),
            None,
        )

    def find_all(self, **filters):
        """Return all objects matching every supplied filter."""
        return [
            obj
            for obj in self._storage.values()
            if self._matches(obj, filters)
        ]

    @staticmethod
    def _matches(obj, filters):
        return all(
            hasattr(obj, attr_name)
            and getattr(obj, attr_name) == attr_value
            for attr_name, attr_value in filters.items()
        )

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if obj is None:
            return None
        obj.update(data)
        return obj

    def delete(self, obj_id):
        return self._storage.pop(obj_id, None)

    def get_by_attribute(self, attr_name, attr_value):
        return self.find_one(**{attr_name: attr_value})

    def clear(self):
        self._storage.clear()
