import json
from collections.abc import Callable

from fastapi.websockets import WebSocket, WebSocketDisconnect

from app.core.logger import logger
from app.schemas.user import UserIDSchema
from app.utils.exceptions import ClientNotConnectedError, InstantiationNotAllowedError
from app.utils.types import IDType


class WebsocketConnectionManager:
    connections: dict[IDType, WebSocket] = {}

    def __init__(self) -> None:
        raise InstantiationNotAllowedError(self.__class__.__name__)

    @classmethod
    def is_connected(cls, id: UserIDSchema) -> bool:
        return id in cls.connections

    @classmethod
    async def send_to(cls, user: UserIDSchema, json_data: object) -> None:
        try:
            await cls.connections[user.id].send_json(json_data)
        except KeyError as error:
            raise ClientNotConnectedError(str(user.id)) from error

    @classmethod
    async def handle_connection(
        cls,
        user: UserIDSchema,
        websocket: WebSocket,
        recv_callback: Callable[[object], None] | None = None,
    ) -> None:
        await websocket.accept()
        cls.connections[user.id] = websocket

        try:
            while True:
                await cls.__handle_recv(websocket, recv_callback)

        except WebSocketDisconnect:
            cls.connections.pop(user.id)

    @classmethod
    async def __handle_recv(
        cls,
        websocket: WebSocket,
        recv_callback: Callable[[object], None] | None = None,
    ) -> None:
        payload = await websocket.receive_text()

        try:
            data = json.loads(payload)
            if recv_callback:
                recv_callback(data)

        except json.JSONDecodeError:
            logger.error(
                "Error decoding JSON payload on websocket "
                f" connection recv. id={id}, payload={payload}"
            )
