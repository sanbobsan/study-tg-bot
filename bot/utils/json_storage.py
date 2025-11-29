import json
import logging

import aiofiles

QUEUES_FILE_PATH = "data/queues.json"


async def load_queues() -> dict[str, list[int]]:
    """Возвращает очереди из файла"""
    try:
        async with aiofiles.open(QUEUES_FILE_PATH, mode="r") as f:
            string: str = await f.read()
        data: dict[str, list[int]] = json.loads(string)
        logging.info("Queue loaded from file")
        return data

    except Exception as e:
        logging.error(e)
        return dict()


async def save_queues(data: dict[str, list[int]]) -> None:
    """Сохраняет очереди в файл"""
    json_string: str = json.dumps(data, indent=4)
    try:
        async with aiofiles.open(QUEUES_FILE_PATH, mode="w") as f:
            await f.write(json_string)
        logging.info("Queue saved to file")

    except Exception as e:
        logging.error(e)
