from collections.abc import Sequence
from typing import Literal

from app.db.repositories import UserRepository

from . import BaseService


class UserDiscoveryService(BaseService):
    async def search_users(
        self,
        *,
        contains: str,
        by: Literal["username", "fullname"],
        count: int | None = None,
    ) -> Sequence[str]:
        async with self.uow as uow:
            model = UserRepository.model_cls
            attr = model.fullname if by == "fullname" else model.username
            return await uow.userRepository.get_column_scalars(attr, contains, count)
