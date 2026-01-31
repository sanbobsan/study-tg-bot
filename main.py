import asyncio
import logging
from asyncio.exceptions import CancelledError

from bot.create_bot import bot, dp
from bot.db import create_tables
from bot.handlers import main_router
from bot.utils.queue import QueueManager

queue_manager = QueueManager()


async def start_bot() -> None:
    await create_tables()
    await queue_manager.load_from_file()


async def main() -> None:
    try:
        dp.include_router(main_router)
        dp.startup.register(start_bot)

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    except CancelledError:
        logging.info("Bot turned off by cancel, handled CancelledError")

    finally:
        await bot.session.close()
        await queue_manager.save_to_file()


if __name__ == "__main__":
    asyncio.run(main())
