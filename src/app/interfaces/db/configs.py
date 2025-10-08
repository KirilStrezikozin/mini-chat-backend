from abc import ABC, abstractmethod
from typing import ClassVar

from pydantic import BaseModel


class AbstractDatabaseConfig(ABC, BaseModel):
    name: ClassVar[str]

    @property
    @abstractmethod
    def uri(self) -> str:
        """
        Returns the connection URI for this database configuration.
        """
        ...
