from decouple import config


class Config:
    TOKEN = config("TOKEN")
    ADMINS = [int(admin_id) for admin_id in config("ADMINS").split(",")]


config = Config
