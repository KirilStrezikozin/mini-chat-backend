import json
from collections.abc import Callable

from fastapi.websockets import WebSocket, WebSocketDisconnect

from app.core.logger import logger
from app.schemas.user import UserIDSchema
from app.utils.exceptions import (
    ClientNotConnectedError,
    InstantiationNotAllowedError,
    WebSocketClientAlreadyConnected,
)
from app.utils.types import IDType


class WebsocketConnectionManager:
    connections: dict[IDType, WebSocket] = {}

    def __init__(self) -> None:
        raise InstantiationNotAllowedError(self.__class__.__name__)

    @classmethod
    def is_connected(cls, user: UserIDSchema) -> bool:
        return user.id in cls.connections

    @classmethod
    async def send_to(cls, user: UserIDSchema, data: str) -> None:
        try:
            await cls.connections[user.id].send_text(data)

            logger.info(
                f"{cls.__name__}: {data} sent to {user.id}",
            )

        except KeyError as error:
            raise ClientNotConnectedError(str(user.id)) from error

    @classmethod
    async def handle_connection(
        cls,
        *,
        user: UserIDSchema,
        websocket: WebSocket,
        recv_callback: Callable[[object], None] | None = None,
    ) -> None:
        if cls.is_connected(user):
            raise WebSocketClientAlreadyConnected(str(user.id))

        await websocket.accept()
        cls.connections[user.id] = websocket

        logger.info(
            f"{cls.__name__}: connection with client {user.id} accepted",
        )
        logger.info(
            f"{cls.__name__}: connections in pool: {len(cls.connections)}",
        )

        try:
            while True:
                await cls.__handle_recv(websocket, recv_callback)

        except WebSocketDisconnect:
            del cls.connections[user.id]

            logger.info(
                f"{cls.__name__}: connection with client {user.id} closed",
            )
            logger.info(
                f"{cls.__name__}: connections left in pool: {len(cls.connections)}",
            )

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
                f"{cls.__name__}: error decoding JSON payload on websocket "
                f" connection recv. id={id}, payload={payload}"
            )
