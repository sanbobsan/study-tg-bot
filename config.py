from decouple import config  # type: ignore


class Config:
    TOKEN: str = config("TOKEN")
    ADMINS: list[int] = [int(admin_id) for admin_id in config("ADMINS").split(",")]
    STORAGE_PATH: str = config("STORAGE_PATH").rstrip("/")


config = Config
