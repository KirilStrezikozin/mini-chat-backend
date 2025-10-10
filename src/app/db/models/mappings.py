import uuid
from datetime import UTC, datetime
from typing import Annotated

from sqlalchemy.orm import mapped_column

from app.utils.types import IDType

PrimaryKeyID = Annotated[IDType, mapped_column(default=uuid.uuid4, primary_key=True)]

Timestamp = Annotated[datetime, mapped_column(default=datetime.now(UTC))]
