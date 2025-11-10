from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.db.dao import update_user
from bot.keyboards import keyboards as kb
from bot.utils.queue import Queue

router = Router()
queue = Queue()


@router.message(F.text.lower().in_(["меню", "menu"]))
@router.message(Command("menu"))
async def menu(message: Message):
    text = await queue.build_queue_text()
    await message.answer(
        text=text, reply_markup=kb.menu.as_markup(resize_keyboard=True)
    )


@router.message(F.text.lower() == "хочу")
@router.message(Command("yes", "y"))
async def yes(message: Message):
    await update_user(tg_id=message.from_user.id, has_desire=True)
    text = "🟢 Ты добавлен в очередь!\n\n" + await queue.build_queue_text()
    await message.answer(
        text=text,
        reply_markup=kb.menu.as_markup(resize_keyboard=True),
    )


@router.message(F.text.lower() == "не хочу")
@router.message(Command("no", "n"))
async def no(message: Message):
    await update_user(tg_id=message.from_user.id, has_desire=False)
    text = "🔴 Ты удалён из очереди!\n\n" + await queue.build_queue_text()
    await message.answer(
        text=text,
        reply_markup=kb.menu.as_markup(resize_keyboard=True),
    )
