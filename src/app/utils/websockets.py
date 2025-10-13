import json
from collections.abc import Callable, Iterable

from fastapi.websockets import WebSocket, WebSocketDisconnect

from app.core.logger import logger
from app.schemas import (
    MessageDeleteAnnouncementSchema,
    MessagePutAnnouncementSchema,
    UserIDSchema,
)
from app.utils.exceptions import (
    ClientNotConnectedError,
    InstantiationNotAllowedError,
)
from app.utils.types import IDType


class WebSocketConnectionManager:
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
            logger.info(
                f"{cls.__name__}: connection with client {user.id} already established",
            )

            # raise WebSocketClientAlreadyConnected(str(user.id))
            await websocket.close(1000)
            return

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


class WebSocketController:
    def __init__(self) -> None:
        raise InstantiationNotAllowedError(self.__class__.__name__)

    @staticmethod
    async def announce(
        *,
        users: Iterable[UserIDSchema],
        model: MessagePutAnnouncementSchema | MessageDeleteAnnouncementSchema,
        from_user: UserIDSchema | None = None,
    ):
        """
        Sends a JSON representation of the given model to users that are in the
        websocket connection pool, except to optional `from_user`.

        Receivers should check whether the message payload exists in their
        store. If so, update its attributes. Otherwise, add as new.
        """

        for user in users:
            if from_user and user.id == from_user.id:
                continue
            elif not WebSocketConnectionManager.is_connected(user):
                continue
            await WebSocketConnectionManager.send_to(user, model.model_dump_json())
