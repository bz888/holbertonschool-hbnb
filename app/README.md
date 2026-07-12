## Setup

```bash
git clone https://github.com/bz888/holbertonschool-hbnb.git
```

```bash
cd app/
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Tests and Coverage

See the [test catalogue](tests/TEST_CATALOG.md) for the complete list of unit
and integration tests and the behavior covered by each test.

To display the stored coverage report:

```bash
./.venv/bin/coverage report -m
```

### Manual testing

Refer to `test/regression_test_evidence` for all recorded testing for all routes and all status codes.


## SQLAlchemy Relationships

Users, places, reviews, and amenities use bidirectional SQLAlchemy
relationships. All primary and foreign keys are UUID strings stored as
`String(36)`. Deleting a user or place cascades to dependent records, while
soft-deleting a user preserves their reviews and deactivates their places.

### Place Amenity Replacement

Updating `amenity_ids` through `PUT /places/<place_id>` replaces the place's
entire amenity collection. For example, an existing Wi-Fi amenity is removed
if its ID is omitted from the new list. Reviews are not currently accepted by
the place `PUT` route, but equivalent full-replacement behavior could be added
as a future feature.
