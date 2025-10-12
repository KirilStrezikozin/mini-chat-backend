from collections.abc import Iterable

from sqlalchemy import Row

from app.db.models.mappings import PrimaryKeyID
from app.db.repositories import UserRepository
from app.schemas import ChatSearchByType, ChatSearchResultSchema

from . import BaseService


class ChatDiscoveryService(BaseService):
    async def search_users(
        self,
        *,
        contains: str,
        by: ChatSearchByType,
        count: int | None = None,
    ) -> Iterable[ChatSearchResultSchema]:
        async with self.uow as uow:
            model = UserRepository.model_cls
            attr = model.fullname if by.value == "fullname" else model.username

            res = await uow.userRepository.get_column_scalars(
                (model.id, model.fullname, model.username),
                attr,
                contains.lower(),
                count,
            )

            def transform(row: Row[tuple[PrimaryKeyID, str, str]]):
                resource = row.tuple()
                return ChatSearchResultSchema(
                    id=resource[0],
                    fullname=resource[1],
                    username=resource[2],
                )

            return map(transform, res)
