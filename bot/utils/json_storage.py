import json
import logging
from typing import TypedDict

import aiofiles

from config import config

QUEUES_FILE_PATH = config.STORAGE_PATH + "/queues.json"
BOT_SETTINGS_FILE_PATH = config.STORAGE_PATH + "/bot-settings.json"


class BotSettings(TypedDict):
    """Настройки бота, которые меняются внутри него"""

    trust_new: bool


async def load_queues() -> dict[str, list[int]]:
    """Возвращает очереди из файла"""
    try:
        async with aiofiles.open(QUEUES_FILE_PATH, mode="r") as f:
            string: str = await f.read()
        data: dict[str, list[int]] = json.loads(string)
        logging.info("Queues loaded from file")
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
        logging.info("Queues saved to file")

    except Exception as e:
        logging.error(e)


async def load_bot_settings() -> BotSettings:
    """Возвращает настройки бота из файла"""
    try:
        async with aiofiles.open(BOT_SETTINGS_FILE_PATH, mode="r") as f:
            string: str = await f.read()
        settings: BotSettings = json.loads(string)
        logging.info("Bot settings loaded from file")
        return settings

    except FileNotFoundError:
        return {"trust_new": True}

    except Exception as e:
        logging.error(e)
        return {"trust_new": True}


async def save_bot_settings(settings: BotSettings) -> None:
    """Сохраняет очереди в файл"""
    json_string: str = json.dumps(settings, indent=4)
    try:
        async with aiofiles.open(BOT_SETTINGS_FILE_PATH, mode="w") as f:
            await f.write(json_string)
        logging.info("Bot settings saved to file")

    except Exception as e:
        logging.error(e)
