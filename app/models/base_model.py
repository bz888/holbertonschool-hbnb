import uuid
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# declarative base class
class Base(DeclarativeBase):
    pass

class BaseModel(Base):
    """Base class for all HBnB domain models."""
    __abstract__ = True

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.timezone.utc
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.timezone.utc,
        onupdate=datetime.timezone.utc
    )

    def update(self, data: dict) -> None:
        """Update object attributes from a dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
