from pydantic import BaseModel, ConfigDict

from app.utils.types import IDType


class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IDSchema(Base):
    id: IDType
