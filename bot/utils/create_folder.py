from pathlib import Path


def create_folder() -> None:
    Path("data").mkdir(exist_ok=True)
