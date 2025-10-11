from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.config import Config
from app.schemas import TokenPayload, TokenSchema, TokenType, UserIDSchema
from app.utils.exceptions import TokenValidationError
from app.utils.security import JWTManager, ResponseCookieManager


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        config: Config,
        include_paths: set[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.config = config
        self.include_paths = include_paths or set()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path not in self.include_paths:
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
            idSchema = UserIDSchema(id=refresh_token_payload.id)
            refresh_schema = JWTManager.create_token_schema(self.config, idSchema)
            token_payload = TokenPayload(id=idSchema.id, type=TokenType.access_token)

        if not token_payload:
            return Response("Unauthorized", status_code=401)

        JWTManager.set_request_token_payload(request, token_payload)
        response = await call_next(request)

        if refresh:
            # If tokens were refreshed, update cookies.
            assert refresh_schema
            cookie_manager = ResponseCookieManager(self.config, response)
            cookie_manager.set_token_cookie(refresh_schema)

        return response
