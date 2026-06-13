import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.amenity import Amenity


class TestAmenity(unittest.TestCase):
    def test_create_valid_amenity(self):
        amenity = Amenity("Wi-Fi")

        self.assertEqual(amenity.name, "Wi-Fi")

    def test_to_dict(self):
        amenity = Amenity("Parking")

        self.assertEqual(amenity.to_dict()["name"], "Parking")


if __name__ == "__main__":
    unittest.main()
