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

## Docker Compose

Create a local environment file before starting the containers:

```bash
cp .env.example .env
```

Keep `.env` private. For development, set `SECRET_KEY` and `JWT_SECRET_KEY`
to local testing values. Before running the production configuration, replace
all placeholder values with strong, unique secrets.

### Development with SQLite

The default Compose configuration runs Flask with a SQLite database stored at
`data/sqlite/hbnb.sqlite3`. MySQL is not started or required during
development.

```bash
docker compose up --build
```

To open the persisted development database with the pinned SQLite CLI:

```bash
docker compose --profile sqlite-tools run --rm sqlite3 /data/hbnb.sqlite3
```

### Production with MySQL

The production override changes Flask's `DATABASE_URL` to MySQL and starts a
MySQL container. Set `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, and
`MYSQL_ROOT_PASSWORD` in `.env`, then run:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  up --build -d
```

To stop either stack, use the same Compose file arguments with `down`. For
example, stop the production stack with:

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod.yml \
  down
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
