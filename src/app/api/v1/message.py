from fastapi import HTTPException

from app.api.deps import EditMessageServiceDependency
from app.schemas import MessageEditSchema, MessageIDSchema
from app.services.exceptions import MessageNotFoundError
from app.utils.router import APIRouterWithRouteProtection

message_router = APIRouterWithRouteProtection(prefix="/message", tags=["message"])


@message_router.post("/edit", protected=True)
async def edit_message(
    service: EditMessageServiceDependency,
    editSchema: MessageEditSchema,
):
    # TODO: websocket
    try:
        await service.edit(editSchema=editSchema)
    except MessageNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail) from error


@message_router.post("/delete", protected=True)
async def delete_message(
    service: EditMessageServiceDependency, idSchema: MessageIDSchema
):
    # TODO: websocket
    try:
        await service.delete(idSchema=idSchema)
    except MessageNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail) from error
