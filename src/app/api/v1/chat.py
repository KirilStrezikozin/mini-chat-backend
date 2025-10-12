from fastapi import APIRouter

from app.api.deps import ChatDiscoveryServiceDependency
from app.schemas import ChatSearchByType, ChatSearchResultSchema

chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.get("/search/{by}")
async def search(
    service: ChatDiscoveryServiceDependency,
    contains: str,
    by: ChatSearchByType,
    count: int | None = None,
) -> list[ChatSearchResultSchema]:
    res = await service.search_users(contains=contains, by=by, count=count)
    return list(res)
