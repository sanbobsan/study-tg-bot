from pathlib import Path


def create_folder(path: str) -> None:
    Path(path).mkdir(exist_ok=True)
