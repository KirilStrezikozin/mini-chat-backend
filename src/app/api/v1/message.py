from fastapi import HTTPException

from app.api.deps import (
    ChatServiceDependency,
    MessageServiceDependency,
)
from app.schemas import (
    ChatIDSchema,
    MessageDeleteAnnouncementSchema,
    MessageDeleteSchema,
    MessageEditSchema,
    MessagePutAnnouncementSchema,
    MessageReadSchema,
)
from app.services.exceptions import MessageNotFoundError
from app.utils.exceptions import ClientNotConnectedError
from app.utils.router import APIRouterWithRouteProtection
from app.utils.websockets import WebSocketController

message_router = APIRouterWithRouteProtection(prefix="/message", tags=["message"])


@message_router.post("/edit", protected=True)
async def edit_message(
    message_service: MessageServiceDependency,
    chat_service: ChatServiceDependency,
    message_schema: MessageEditSchema,
) -> None:
    try:
        message = await message_service.get(message_schema=message_schema)
        await message_service.edit(message_schema=message_schema)

        chat_users = await chat_service.get_users(
            chatIDSchema=ChatIDSchema(id=message.chat_id)
        )

        await WebSocketController.announce(
            users=chat_users,
            model=MessagePutAnnouncementSchema(
                message=MessageReadSchema(
                    id=message.id,
                    chat_id=message.chat_id,
                    sender_id=message.sender_id,
                    content=message_schema.content,
                    timestamp=message.timestamp,
                )
            ),
        )

    except MessageNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail) from error
    except ClientNotConnectedError:
        pass


@message_router.post("/delete", protected=True)
async def delete_message(
    message_service: MessageServiceDependency,
    chat_service: ChatServiceDependency,
    message_schema: MessageDeleteSchema,
) -> None:
    try:
        message = await message_service.get(message_schema=message_schema)
        await message_service.delete(message_schema=message_schema)

        chat_users = await chat_service.get_users(
            chatIDSchema=ChatIDSchema(id=message.chat_id)
        )

        await WebSocketController.announce(
            users=chat_users,
            model=MessageDeleteAnnouncementSchema(message=message_schema),
        )

    except MessageNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail) from error
    except ClientNotConnectedError:
        pass
