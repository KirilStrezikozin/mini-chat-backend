from typing import override

from fastapi import Request, Response, status
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.config import Config
from app.core.exceptions import TokenValidationError
from app.schemas import TokenPayload, TokenSchema, TokenType, UserIDSchema
from app.utils.security import HTTPResponseCookieManager, JWTManager


class AuthenticationMiddleware(BaseHTTPMiddleware):
    @override
    def __init__(self, app: ASGIApp, config: Config) -> None:
        super().__init__(app)
        self.config = config

    @override
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        protected = False
        route = request.scope["route"]
        if isinstance(route, APIRoute):
            protected = getattr(route, "protected", False)

        if not protected:
            return await call_next(request)

        access_token = request.cookies.get(TokenType.access_token.value)
        refresh_token = request.cookies.get(TokenType.refresh_token.value)

        token_payload: TokenPayload | None = None

        refresh_token_payload: TokenPayload | None = None
        refresh_schema: TokenSchema | None = None
        refresh = False

        try:
            if access_token:
                token_payload = JWTManager.validate_token(
                    self.config, access_token, TokenType.access_token
                )
        except TokenValidationError:
            pass

        try:
            if not token_payload and refresh_token:
                refresh_token_payload = JWTManager.validate_token(
                    self.config, refresh_token, TokenType.refresh_token
                )
                refresh = True
        except TokenValidationError:
            pass

        if refresh:
            assert refresh_token_payload
            user_schema = UserIDSchema(id=refresh_token_payload.id)
            refresh_schema = JWTManager.create_token_schema(self.config, user_schema)
            token_payload = TokenPayload(id=user_schema.id, type=TokenType.access_token)

        if not token_payload:
            return Response("Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

        JWTManager.set_request_token_payload(request, token_payload)
        response = await call_next(request)

        if refresh:
            # If tokens were refreshed, update cookies.
            assert refresh_schema
            cookie_manager = HTTPResponseCookieManager(self.config, response)
            cookie_manager.set_token_cookie(refresh_schema)

        return response
