import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.data_base.base import create_tables
from bot.handlers.start import start_router
from bot.handlers.register import register_router
from config import TOKEN


async def start_bot():
    await create_tables()


async def main():
    try:
        bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp = Dispatcher(storage=MemoryStorage())

        dp.include_router(start_router)
        dp.include_router(register_router)
        dp.startup.register(start_bot)

        print("!!! Bot turned on !!!")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    except Exception as e:
        print(f"!!! Error !!! \n{e}\n")

    finally:
        await bot.session.close()
        print("!!! Bot turned off !!!")


if __name__ == "__main__":
    asyncio.run(main())
