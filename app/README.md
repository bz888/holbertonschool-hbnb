## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Tests and Coverage

See the [test catalogue](tests/TEST_CATALOG.md) for the complete list of unit
and integration tests and the behavior covered by each test.

To display the stored coverage report:

```bash
./venv/bin/coverage report -m
```

## Current Relationship Shortfalls

### Loose Relationship References

Hard deletion can leave stale in-memory references between users, places,
amenities, and reviews. The `/places/<place_id>/reviews` route currently
supports only `GET` and `POST`; a future `PUT` route could support replacing a
place's complete review collection.

### Full Replacement with Place PUT

Updating `amenity_ids` through `PUT /places/<place_id>` replaces the place's
entire amenity collection. For example, an existing Wi-Fi amenity is removed
if its ID is omitted from the new list. Reviews are not currently accepted by
the place `PUT` route, but equivalent full-replacement behavior could be added
as a future feature.
