from pydantic import BaseModel

from app.utils.types import IDType


class IDSchema(BaseModel):
    id: IDType
