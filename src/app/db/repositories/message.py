from collections.abc import Sequence

from sqlalchemy import ColumnElement, and_, select
from sqlalchemy.sql.elements import BinaryExpression

from app.db.models import MessageModel
from app.db.repositories import GenericRepository
from app.interfaces.db.repositories import AbstractMessageRepository
from app.schemas import (
    MessageCreateSchema,
    MessageFetchSchema,
    MessageIDSchema,
)


class MessageRepository(
    AbstractMessageRepository,
    GenericRepository[MessageModel, MessageIDSchema, MessageCreateSchema],
    model=MessageModel,
):
    async def fetch_messages(
        self, *, message_fetch_schema: MessageFetchSchema
    ) -> Sequence[MessageModel]:
        [chat_id, since, until, count] = [
            message_fetch_schema.chat_id,
            message_fetch_schema.since,
            message_fetch_schema.until,
            message_fetch_schema.count,
        ]

        period_clause: BinaryExpression[bool] | ColumnElement[bool]
        if since and until:
            period_clause = self.model_cls.timestamp.between(since, until)
        elif since:
            period_clause = self.model_cls.timestamp > since
        else:
            assert until is not None
            period_clause = self.model_cls.timestamp < until

        stmt = select(self.model_cls).where(
            and_(
                self.model_cls.chat_id == chat_id,
                period_clause,
            )
        )

        if since:
            stmt = stmt.order_by(self.model_cls.timestamp.asc())
        else:
            stmt = stmt.order_by(self.model_cls.timestamp.desc())

        if count:
            stmt = stmt.limit(count)

        result = await self._session.execute(stmt)
        return result.scalars().all()
