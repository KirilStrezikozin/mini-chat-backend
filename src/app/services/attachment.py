from collections.abc import Iterable
from typing import override

from app.core.config import Config
from app.core.exceptions import (
    AttachmentNotFoundError,
)
from app.interfaces.utils.s3.client import S3ClientProtocol
from app.interfaces.utils.uow import AbstractAsyncUnitOfWork
from app.schemas import (
    AttachmentCreateSchema,
    AttachmentIDSchema,
    AttachmentReadSchema,
    ChatIDSchema,
)

from .base import BaseService


class AttachmentService(BaseService):
    @override
    def __init__(
        self,
        config: Config,
        uow: AbstractAsyncUnitOfWork,
        s3: S3ClientProtocol,
    ) -> None:
        super().__init__(config, uow)
        self.s3 = s3

    async def get(self, *, attachment_schema: AttachmentIDSchema) -> str:
        async with self.uow as uow:
            resource = await uow.attachmentRepository.get(attachment_schema)
            if not resource:
                raise AttachmentNotFoundError

            attachment = AttachmentReadSchema.model_validate(resource)

            return self.s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.config.s3.BUCKET_NAME,
                    "Key": str(attachment.id),
                },
                ExpiresIn=self.config.s3.PRESIGNED_URL_EXPIRES_IN,
            )

    async def add_and_get_presigned_urls(
        self, *, attachment_schemas: Iterable[AttachmentCreateSchema]
    ) -> tuple[list[AttachmentReadSchema], list[str]]:
        async with self.uow as uow:
            resources = await uow.attachmentRepository.add_many(attachment_schemas)

            def gen_url(attachment: AttachmentIDSchema):
                return self.s3.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={
                        "Bucket": self.config.s3.BUCKET_NAME,
                        "Key": str(attachment.id),
                    },
                    ExpiresIn=self.config.s3.PRESIGNED_URL_EXPIRES_IN,
                )

            attachments = [AttachmentReadSchema.model_validate(v) for v in resources]
            presigned_urls = [gen_url(v) for v in attachments]
            return (attachments, presigned_urls)

    async def get_all_in_chat(
        self, *, chat_schema: ChatIDSchema
    ) -> list[AttachmentReadSchema]:
        async with self.uow as uow:
            # Ensure the requested chat exists.
            _ = await self._get_chat_resource(uow, chat_schema)
            resources = await uow.attachmentRepository.get_all_in_chat(
                chat_schema=chat_schema
            )

            return [AttachmentReadSchema.model_validate(v) for v in resources]
