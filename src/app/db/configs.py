from pydantic import BaseModel, PostgresDsn, computed_field

from app.interfaces.db.configs import AbstractDatabaseConfig


class PostgresDsnConfig(AbstractDatabaseConfig):
    name = "postgres"

    POSTGRES_SCHEME: str = "postgresql+asyncpg"
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @computed_field
    @property
    def uri(self) -> str:
        return str(
            PostgresDsn.build(
                scheme=self.POSTGRES_SCHEME,
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )


class AwsS3BucketConfig(BaseModel):
    ENDPOINT_URL: str
    ACCESS_KEY_ID: str
    SECRET_ACCESS_KEY: str
    SIGNATURE_VERSION: str = "s3v4"
    REGION_NAME: str = "auto"
    BUCKET_NAME: str
    PRESIGNED_URL_EXPIRES_IN: int = 30


"""Available database configuration classes keyed by name."""
database_configs = {
    PostgresDsnConfig.name: PostgresDsnConfig,
}
