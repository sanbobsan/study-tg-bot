from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot import keyboards as kb
from bot.db import get_user, update_user
from bot.middlewares import IsTrustedMiddleware
from bot.utils.queue import QueueManager

queue_manager = QueueManager()

router = Router()
router.message.middleware(IsTrustedMiddleware(get_user_func=get_user))


@router.message(F.text.lower().in_(["меню", "menu"]))
@router.message(Command("menu"))
async def menu(message: Message):
    text = await queue_manager.queue_show()
    await message.answer(
        text=text, reply_markup=kb.menu.as_markup(resize_keyboard=True)
    )


@router.message(F.text.lower() == "хочу")
@router.message(Command("yes", "y"))
async def yes(message: Message):
    await process_desire(message, desire=True)


@router.message(F.text.lower() == "не хочу")
@router.message(Command("no", "n"))
async def no(message: Message):
    await process_desire(message, desire=False)


async def process_desire(message: Message, desire: bool):
    if message.from_user is None:
        return
    await update_user(tg_id=message.from_user.id, has_desire=desire)
    await queue_manager.queue_update_cached_text()
    text: str = (
        f"{'🟢 Ты добавлен в очередь!' if desire else '🔴 Ты удалён из очереди!'}\n\n"
        + (await queue_manager.queue_show())
    )
    await message.answer(
        text=text,
        reply_markup=kb.menu.as_markup(resize_keyboard=True),
    )
