from typing import Protocol


class S3ClientProtocol(Protocol):
    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: dict | None = None,
        ExpiresIn: int = 3600,
        HttpMethod: str | None = None,
    ) -> str: ...
