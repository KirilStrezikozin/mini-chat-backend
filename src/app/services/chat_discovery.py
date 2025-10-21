from sqlalchemy import Row

from app.db.models.mappings import PrimaryKeyID
from app.schemas import ChatSearchByType, ChatSearchResultSchema, UserIDSchema

from .base import BaseService


class ChatDiscoveryService(BaseService):
    async def search_users(
        self,
        *,
        contains: str,
        by: ChatSearchByType,
        skip_id: UserIDSchema,
        count: int | None = None,
    ) -> list[ChatSearchResultSchema]:
        async with self.uow as uow:
            resource = await uow.userRepository.search_by(contains, by, skip_id, count)

            def make_search_result(row: Row[tuple[PrimaryKeyID, str, str]]):
                resource = row.tuple()
                return ChatSearchResultSchema(
                    id=resource[0],
                    fullname=resource[1],
                    username=resource[2],
                )

            return [make_search_result(v) for v in resource]
