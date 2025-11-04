from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.keyboards import admin as kb
from bot.utils.queue import Queue
from config import config

router = Router()
queue = Queue()


# TODO: управление очередью админ панелью
# TODO: фильтр для админ панели
# TODO: оповещения людей, когда очередь создается
@router.message(F.text, Command("admin", "adm"), F.from_user.id.in_(config.ADMINS))
async def admin_panel(message: Message):
    await message.answer(
        "ADMIN PANEL\n/cr, /sh, /next",
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(F.text, Command("create", "cr"), F.from_user.id.in_(config.ADMINS))
async def create(message: Message):
    await queue.create_queue()
    text = "Created\n" + str(await queue.build_queue_text())
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(
    F.text, Command("shuffle", "shf", "sh"), F.from_user.id.in_(config.ADMINS)
)
async def admin_shuffle(message: Message):
    queue.shuffle()
    text = "Shuffled\n" + str(await queue.build_queue_text())
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(F.text, Command("next"), F.from_user.id.in_(config.ADMINS))
async def next(message: Message):
    await queue.next()
    text = "Nexted\n" + str(await queue.build_queue_text())
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )
