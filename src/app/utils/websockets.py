import json
import logging
from collections import defaultdict
from collections.abc import Callable, Iterable

from fastapi import status
from fastapi.datastructures import Address
from fastapi.websockets import WebSocket, WebSocketDisconnect

from app.core.exceptions import (
    InstantiationNotAllowedError,
    WebSocketNoClientError,
)
from app.core.logger import root_logger
from app.schemas import (
    MessageAttachmentsAnnouncementSchema,
    MessageDeleteAnnouncementSchema,
    MessagePutAnnouncementSchema,
    UserIDSchema,
)
from app.utils.types import IDType

logger = root_logger.getChild("utils.websockets")


class WebSocketManager:
    users: dict[IDType, dict[Address, WebSocket]] = defaultdict(dict)
    logger = logger.getChild("manager")

    def __init__(self) -> None:
        raise InstantiationNotAllowedError(self.__class__.__name__)

    @classmethod
    def log_users(cls) -> None:
        print(cls.logger.level)
        if cls.logger.level <= logging.DEBUG:
            for user_id, clients in cls.users.items():
                cls.logger.debug(f"{user_id} - user in pool, {len(clients)} clients")

    @classmethod
    async def accept_client(cls, user: UserIDSchema, websocket: WebSocket) -> Address:
        client = websocket.client
        if not client:
            raise WebSocketNoClientError

        await websocket.accept()
        cls.users[user.id][client] = websocket

        cls.logger.debug(f"{user.id} - {client} - accepted")
        cls.log_users()

        return client

    @classmethod
    def close_client(cls, user: UserIDSchema, client: Address) -> None:
        cls.users[user.id].pop(client)

        cls.logger.debug(f"{user.id} - {client} - client closed")
        cls.log_users()

    @classmethod
    async def close_user(cls, user: UserIDSchema) -> None:
        clients = cls.users.pop(user.id)
        for websocket in clients.values():
            await websocket.close(status.WS_1000_NORMAL_CLOSURE)

        cls.logger.debug(f"{user.id} - closed all clients")
        cls.log_users()

    @classmethod
    async def send_to_user(cls, user: UserIDSchema, data: str) -> None:
        clients = cls.users[user.id]
        for websocket in clients.values():
            await websocket.send_text(data)

        cls.logger.debug(f"{user.id} - broadcasted {data} to {len(clients)} clients")

    @classmethod
    async def handle_client(
        cls,
        *,
        user: UserIDSchema,
        websocket: WebSocket,
        recv_callback: Callable[[object], None] | None = None,
    ) -> None:
        client = await cls.accept_client(user, websocket)

        try:
            while True:
                payload = await websocket.receive_text()

                try:
                    data = json.loads(payload)
                    if recv_callback:
                        recv_callback(data)
                except json.JSONDecodeError:
                    cls.logger.error(f"{user.id} - {client} - error decoding {payload}")

        except WebSocketDisconnect:
            cls.close_client(user, client)

    @classmethod
    async def announce(
        cls,
        *,
        users: Iterable[UserIDSchema],
        model: MessagePutAnnouncementSchema
        | MessageDeleteAnnouncementSchema
        | MessageAttachmentsAnnouncementSchema,
    ):
        """
        Sends a JSON representation of the given model to users that are in the
        websocket connection pool.

        Receivers should check whether the message payload exists in their
        store. If so, update its attributes. Otherwise, add as new.
        """

        data = model.model_dump_json()
        for user in users:
            if user.id not in cls.users:
                continue
            await cls.send_to_user(user, data)
