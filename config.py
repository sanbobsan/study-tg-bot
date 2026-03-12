from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    token: str = Field()
    admins: list[int] = Field()

    storage_path: str = "data"

    db_user: str = "user"
    db_password: SecretStr = Field()
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "database"

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password.get_secret_value()}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()  # type: ignore
