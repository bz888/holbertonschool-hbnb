import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.base_model import BaseModel


class TestBaseModel(unittest.TestCase):
    def test_base_model_has_id_and_timestamps(self):
        model = BaseModel()

        self.assertIsInstance(model.id, str)
        self.assertIsInstance(model.created_at, datetime)
        self.assertIsInstance(model.updated_at, datetime)

    def test_save_updates_updated_at(self):
        model = BaseModel()
        old_updated_at = model.updated_at

        model.save()

        self.assertGreaterEqual(model.updated_at, old_updated_at)

    def test_update_sets_existing_attributes(self):
        model = BaseModel()
        model.name = "Old"

        model.update({"name": "New", "missing": "ignored"})

        self.assertEqual(model.name, "New")
        self.assertFalse(hasattr(model, "missing"))


if __name__ == "__main__":
    unittest.main()
