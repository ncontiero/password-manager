from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Password(SQLModel, table=True):
    id: int = Field(primary_key=True)
    domain: str = Field(index=True, unique=True)
    password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
