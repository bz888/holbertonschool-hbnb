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

The development Compose configuration selects `DevelopmentConfig` and stores
its SQLite database at `data/sqlite/hbnb.sqlite3`. MySQL is not started or
required.

```bash
docker compose up --build
```

To open the persisted development database with the pinned SQLite CLI:

```bash
docker compose --profile sqlite-tools run --rm sqlite3 /data/hbnb.sqlite3
```

### MySQL Compatibility Mode

The standalone production Compose configuration selects `ProductionConfig`
and runs the same Flask application against MySQL. This mode is for verifying
database compatibility locally; it is not intended as an internet-facing
deployment.

Stop the development stack first because both modes publish port `8080`:

```bash
docker compose down
```

Set `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, and
`MYSQL_ROOT_PASSWORD` in `.env`, then start MySQL mode:

```bash
docker compose -f docker-compose.prod.yml up --build
```

To switch back to SQLite, stop MySQL mode without removing its named database
volume, then start development again:

```bash
docker compose -f docker-compose.prod.yml down
docker compose up --build
```

SQLite uses `seeds/seed.sqlite.sql`, while MySQL uses
`seeds/seed.mysql.sql`. Both seed scripts are idempotent and are selected from
the active SQLAlchemy dialect.

If the MySQL credentials in `.env` change, recreate the local compatibility
database so MySQL can initialize it with the new values. This deletes all data
stored in the MySQL-mode named volume:

```bash
docker compose -f docker-compose.prod.yml down --volumes
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
