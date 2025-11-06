from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.keyboards import admin as kb
from bot.utils.queue import Queue
from config import config

router = Router()
queue = Queue()


# TODO: свой полноценный фильтр для админ панели
@router.message(Command("admin", "adm"), F.from_user.id.in_(config.ADMINS))
async def admin_panel(message: Message):
    text = "⚙️ Панель администратора ⚙️\n\nДоступные команды:\n• /create — создать очередь\n• /shuffle — перемешать очередь\n• /next — перейти к следующему"
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(Command("create", "cr"), F.from_user.id.in_(config.ADMINS))
async def adm_create(message: Message):
    await queue.create_queue()
    text = "↩️ Очередь успешно создана! ⚙️\n\n" + str(await queue.build_queue_text())
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(Command("shuffle", "shf", "sh"), F.from_user.id.in_(config.ADMINS))
async def adm_shuffle(message: Message):
    queue.shuffle()
    text = "🔀 Очередь перемешана! ⚙️\n\n" + str(await queue.build_queue_text())
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(Command("next"), F.from_user.id.in_(config.ADMINS))
async def adm_next(message: Message):
    await queue.next()
    text = "➡️ Переход к следующему выполнен! ⚙️\n\n" + str(
        await queue.build_queue_text()
    )
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


# TODO: /rename, /change name, /change desire, /trust, /get_ids управление очередью админ панелью
# TODO: /notify, оповещения людей, когда очередь создается
