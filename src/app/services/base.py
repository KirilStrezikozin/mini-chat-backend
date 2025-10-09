from app.core.config import Config
from app.utils.uow import AsyncUnitOfWork


class BaseService:
    def __init__(self, config: Config, uow: AsyncUnitOfWork) -> None:
        self.config = config
        self.uow = uow
