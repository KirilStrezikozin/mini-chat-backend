from app.api.deps import (
    AttachmentServiceDependency,
    ChatServiceDependency,
    MessageServiceDependency,
)
from app.core.router import ProtectedAPIRouter
from app.schemas import (
    AttachmentCreateSchema,
    ChatIDSchema,
    MessageAttachmentsAnnouncementSchema,
    MessageContentSchema,
    MessageDeleteAnnouncementSchema,
    MessageEditSchema,
    MessageIDSchema,
    MessagePutAnnouncementSchema,
    MessageReadSchema,
    PresignedAttachmentsReadSchema,
)
from app.utils.types import IDType
from app.utils.websockets import WebSocketManager

protected_router = ProtectedAPIRouter(prefix="/messages", tags=["messages"])


@protected_router.patch("/{id}")
async def edit_message(
    chat_service: ChatServiceDependency,
    message_service: MessageServiceDependency,
    id: IDType,
    content_schema: MessageContentSchema,
) -> MessageReadSchema:
    message = await message_service.patch(
        message_schema=MessageEditSchema(id=id, content=content_schema.content)
    )

    chat_users = await chat_service.get_users(
        chat_schema=ChatIDSchema(id=message.chat_id)
    )

    await WebSocketManager.announce(
        users=chat_users, model=MessagePutAnnouncementSchema(message=message)
    )

    return message


@protected_router.delete("/{id}")
async def delete_message(
    message_service: MessageServiceDependency,
    chat_service: ChatServiceDependency,
    id: IDType,
) -> None:
    message_schema = MessageIDSchema(id=id)
    message = await message_service.get(message_schema=message_schema)
    await message_service.delete(message_schema=message_schema)

    chat_users = await chat_service.get_users(
        chat_schema=ChatIDSchema(id=message.chat_id)
    )

    await WebSocketManager.announce(
        users=chat_users,
        model=MessageDeleteAnnouncementSchema(message=message),
    )


@protected_router.post("/{id}/attachments")
async def add_and_presign_attachments(
    message_service: MessageServiceDependency,
    attachment_service: AttachmentServiceDependency,
    id: IDType,
    attachment_schemas: list[AttachmentCreateSchema],
) -> PresignedAttachmentsReadSchema:
    attachments, presigned_urls = await attachment_service.add_and_get_presigned_urls(
        attachment_schemas=attachment_schemas
    )

    users = await message_service.get_users_of_chat(
        message_schema=MessageIDSchema(id=id)
    )

    await WebSocketManager.announce(
        users=users,
        model=MessageAttachmentsAnnouncementSchema(attachments=attachments),
    )

    return PresignedAttachmentsReadSchema(urls=presigned_urls, attachments=attachments)
