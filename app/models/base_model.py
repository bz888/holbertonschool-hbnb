import uuid
from datetime import datetime, timezone
from extensions import db


class BaseModel(db.Model):
    """Base class for all HBnB domain models."""
    __abstract__ = True

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __init__(self, **kwargs):
        """Initialize ORM objects with domain-visible UUIDs and timestamps."""
        now = datetime.now(timezone.utc)
        kwargs.setdefault("id", str(uuid.uuid4()))
        kwargs.setdefault("created_at", now)
        kwargs.setdefault("updated_at", now)
        super().__init__(**kwargs)

    def update(self, data):
        """Update object attributes from a dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
