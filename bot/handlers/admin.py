from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.keyboards import admin as kb
from bot.qlogic import Queue
from config import config

router = Router()
queue = Queue()


@router.message(F.text, Command("admin", "adm"), F.from_user.id.in_(config.ADMINS))
async def admin_panel(message: Message):
    await message.answer(
        "ADMIN PANEL", reply_markup=kb.admin.as_markup(resize_keyboard=True)
    )


# TODO: оповещения людей, когда очередь создается
@router.message(
    F.text, Command("shuffle", "shf", "sh"), F.from_user.id.in_(config.ADMINS)
)
async def admin_shuffle(message: Message):
    queue.insert_buffer_into_queue()
    await message.answer(
        "ADMIN PANEL / shuffled", reply_markup=kb.admin.as_markup(resize_keyboard=True)
    )


@router.message(F.text, Command("clear", "clr"), F.from_user.id.in_(config.ADMINS))
async def admin_clear(message: Message):
    queue.clear()
    await message.answer(
        "ADMIN PANEL / cleared", reply_markup=kb.admin.as_markup(resize_keyboard=True)
    )


# TODO: отслеживание текущей очереди
