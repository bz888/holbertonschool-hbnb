import sys
import unittest
import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy import String

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.base_model import BaseModel
from extensions import db
from models.amenity import Amenity
from models.place import Place, place_amenities
from models.review import Review
from models.user import User
from tests.orm_test_case import ORMTestCase


class TestBaseModel(ORMTestCase):
    def test_base_model_has_id_and_timestamps(self):
        model = BaseModel()

        self.assertIsInstance(model.id, str)
        self.assertEqual(str(uuid.UUID(model.id)), model.id)
        self.assertIsInstance(model.created_at, datetime)
        self.assertIsInstance(model.updated_at, datetime)

    def test_base_models_have_unique_ids(self):
        first_model = BaseModel()
        second_model = BaseModel()

        self.assertNotEqual(first_model.id, second_model.id)

    def test_primary_and_foreign_keys_use_uuid_strings(self):
        columns = (
            User.__table__.c.id,
            Place.__table__.c.id,
            Place.__table__.c.owner_id,
            Review.__table__.c.id,
            Review.__table__.c.user_id,
            Review.__table__.c.place_id,
            Amenity.__table__.c.id,
            place_amenities.c.place_id,
            place_amenities.c.amenity_id,
        )

        for column in columns:
            with self.subTest(column=str(column)):
                self.assertIsInstance(column.type, String)
                self.assertEqual(column.type.length, 36)

    def test_commit_updates_updated_at(self):
        amenity = Amenity("Wi-Fi")
        db.session.add(amenity)
        db.session.commit()
        old_updated_at = amenity.updated_at

        amenity.name = "Wireless Internet"
        db.session.commit()

        self.assertGreaterEqual(amenity.updated_at, old_updated_at)

    def test_update_sets_existing_attributes(self):
        model = BaseModel()
        model.name = "Old"

        model.update({"name": "New", "missing": "ignored"})

        self.assertEqual(model.name, "New")
        self.assertFalse(hasattr(model, "missing"))


if __name__ == "__main__":
    unittest.main()
