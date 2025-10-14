from fastapi import HTTPException

from app.api.deps import (
    ChatServiceDependency,
    ConfigDependency,
    MessageServiceDependency,
    S3ClientDependency,
    UserIDDependency,
)
from app.schemas import (
    AttachmentCreateSchema,
    ChatIDSchema,
    MessageAttachmentAnnouncementSchema,
    MessageDeleteAnnouncementSchema,
    MessageDeleteSchema,
    MessageEditSchema,
    MessageIDSchema,
    MessagePutAnnouncementSchema,
    MessageReadSchema,
    PresignedAttachmentReadSchema,
)
from app.services.exceptions import MessageNotFoundError
from app.utils.router import APIRouterWithRouteProtection
from app.utils.types import IDType
from app.utils.websockets import WebSocketManager

message_router = APIRouterWithRouteProtection(prefix="/message", tags=["message"])


@message_router.post("/edit", protected=True)
async def edit_message(
    message_service: MessageServiceDependency,
    chat_service: ChatServiceDependency,
    message_schema: MessageEditSchema,
    user_schema: UserIDDependency,
) -> None:
    try:
        message = await message_service.get(message_schema=message_schema)
        await message_service.edit(message_schema=message_schema)

        chat_users = await chat_service.get_users(
            chatIDSchema=ChatIDSchema(id=message.chat_id)
        )

        await WebSocketManager.announce(
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
            from_user=user_schema,
        )

    except MessageNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail) from error


@message_router.post("/delete", protected=True)
async def delete_message(
    message_service: MessageServiceDependency,
    chat_service: ChatServiceDependency,
    message_schema: MessageDeleteSchema,
    user_schema: UserIDDependency,
) -> None:
    try:
        message = await message_service.get(message_schema=message_schema)
        await message_service.delete(message_schema=message_schema)

        chat_users = await chat_service.get_users(
            chatIDSchema=ChatIDSchema(id=message.chat_id)
        )

        await WebSocketManager.announce(
            users=chat_users,
            model=MessageDeleteAnnouncementSchema(message=message_schema),
            from_user=user_schema,
        )

    except MessageNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail) from error


@message_router.post("/attachment", protected=True)
async def add_and_presign_attachment(
    config: ConfigDependency,
    schema: AttachmentCreateSchema,
    user_schema: UserIDDependency,
    message_service: MessageServiceDependency,
    s3: S3ClientDependency,
) -> PresignedAttachmentReadSchema:
    try:
        attachment = await message_service.add_attachment(schema=schema)

        users = await message_service.get_users_for_message_in_chat(
            message_schema=MessageIDSchema(id=schema.message_id)
        )

        url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": config.s3.BUCKET_NAME,
                "Key": str(attachment.id),
                "ContentType": attachment.content_type,
            },
            ExpiresIn=config.s3.PRESIGNED_URL_EXPIRES_IN,
        )

        await WebSocketManager.announce(
            users=users,
            model=MessageAttachmentAnnouncementSchema(attachment=attachment),
            from_user=user_schema,
        )

        return PresignedAttachmentReadSchema(
            url=url, attachment=attachment, allowed_method="put"
        )

    except MessageNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail) from error


@message_router.get("/attachments", protected=True)
async def get_attachments(
    message_id: IDType,
    message_service: MessageServiceDependency,
):
    try:
        res = await message_service.get_attachments(
            message_schema=MessageIDSchema(id=message_id)
        )
        return list(res)

    except MessageNotFoundError as error:
        raise HTTPException(status_code=404, detail=error.detail) from error
