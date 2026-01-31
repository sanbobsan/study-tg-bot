from pathlib import Path

from config import config


def create_folder() -> None:
    Path(config.STORAGE_PATH).mkdir(exist_ok=True)
