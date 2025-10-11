from pydantic import BaseModel

from app.utils.types import IDType


class Base(BaseModel):
    class Config:
        from_attributes = True


class IDSchema(Base):
    id: IDType
