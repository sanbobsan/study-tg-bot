import asyncio
import logging
from asyncio.exceptions import CancelledError

from bot.create_bot import bot, dp
from bot.data_base.base import create_tables
from bot.handlers import admin, menu, register, start


async def start_bot():
    await create_tables()


async def main():
    try:
        dp.include_routers(start.router, register.router, menu.router)
        dp.include_router(admin.router)
        dp.startup.register(start_bot)

        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    except CancelledError:
        logging.info("Bot turned off by cancel, handled CancelledError")

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
