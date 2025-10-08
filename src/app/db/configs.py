from pydantic import PostgresDsn, computed_field

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


"""Available database configuration classes keyed by name."""
database_configs = {
    PostgresDsnConfig.name: PostgresDsnConfig,
}
