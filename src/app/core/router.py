from typing import override

from fastapi import APIRouter
from fastapi.routing import APIRoute


class ProtectedAPIRoute(APIRoute):
    @override
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.protected = True


class ProtectedAPIRouter(APIRouter):
    @override
    def add_api_route(self, *args, **kwargs) -> None:
        return super().add_api_route(
            *args, **kwargs, route_class_override=ProtectedAPIRoute
        )
