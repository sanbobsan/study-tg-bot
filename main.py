import asyncio

from aiogram import Bot, Dispatcher

from bot.handlers import router
from config import TOKEN


async def main():
    try:
        bot = Bot(token=TOKEN)
        dp = Dispatcher()
        dp.include_router(router)
        print("!!! Bot turned on !!!")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"!!! Error !!! \n{e}\n")
    finally:
        print("!!! Bot turned off !!!")


if __name__ == "__main__":
    asyncio.run(main())
