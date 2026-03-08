from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    token: str = Field()
    admins: list[int] = Field()
    storage_path: str = "data"

    @property
    def db_url(self) -> str:
        path = self.storage_path.rstrip("/")
        return f"sqlite+aiosqlite:///{path}/db.sqlite3"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()  # type: ignore
