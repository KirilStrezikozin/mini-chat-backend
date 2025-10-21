from fastapi.responses import RedirectResponse

from app.api.deps import AttachmentServiceDependency
from app.core.router import ProtectedAPIRouter
from app.schemas import AttachmentIDSchema
from app.utils.types import IDType

protected_router = ProtectedAPIRouter(prefix="/attachments", tags=["attachments"])


@protected_router.get("/{id}")
async def get(id: IDType, attachment_service: AttachmentServiceDependency):
    url = await attachment_service.get(attachment_schema=AttachmentIDSchema(id=id))
    return RedirectResponse(url)
