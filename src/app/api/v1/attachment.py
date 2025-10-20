from fastapi.responses import RedirectResponse

from app.api.deps import (
    AttachmentServiceDependency,
    ConfigDependency,
    S3ClientDependency,
)
from app.schemas import (
    AttachmentIDSchema,
)
from app.utils.router import APIRouterWithRouteProtection
from app.utils.types import IDType

attachment_router = APIRouterWithRouteProtection(
    prefix="/attachment", tags=["attachment"]
)


@attachment_router.get("", protected=True)
async def get(
    config: ConfigDependency,
    id: IDType,
    attachment_service: AttachmentServiceDependency,
    s3: S3ClientDependency,
):
    attachment = await attachment_service.get(
        attachment_schema=AttachmentIDSchema(id=id)
    )

    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": config.s3.BUCKET_NAME,
            "Key": str(attachment.id),
        },
        ExpiresIn=config.s3.PRESIGNED_URL_EXPIRES_IN,
    )

    return RedirectResponse(url)
