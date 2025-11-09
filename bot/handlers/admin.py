from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.db.dao import get_all_users
from bot.db.models import User
from bot.keyboards import admin as kb
from bot.utils.queue import Queue
from config import config

router = Router()
queue = Queue()


# TODO: свой полноценный фильтр для админ панели
@router.message(Command("admin", "adm"), F.from_user.id.in_(config.ADMINS))
async def admin_panel(message: Message):
    """Отправляет админ панелью с доступными командами"""
    text = (
        "⚙️ Панель администратора ⚙️\n"
        "Доступные команды:\n\n"
        "Управление очередью:\n"
        " • /create — создать очередь\n • /shuffle — перемешать очередь\n • /next — перейти к следующему\n\n"
        "Управление пользователями:\n"
        " • /show — показать всех пользователей\n"
    )

    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(Command("create", "cr"), F.from_user.id.in_(config.ADMINS))
async def adm_create(message: Message):
    """Создает очередь из существующих пользователей, отправляет отчет"""
    await queue.create_queue()
    text = "↩️ Очередь успешно создана! ⚙️\n\n" + str(await queue.build_queue_text())
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(Command("shuffle", "shf"), F.from_user.id.in_(config.ADMINS))
async def adm_shuffle(message: Message):
    """Перемешивает существующую очередь, отправляет отчет"""
    queue.shuffle()
    text = "🔀 Очередь перемешана! ⚙️\n\n" + str(await queue.build_queue_text())
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(Command("next"), F.from_user.id.in_(config.ADMINS))
async def adm_next(message: Message):
    """Прокручивает очередь до следующего, отправляет отчет"""
    await queue.next()
    text = "➡️ Переход к следующему выполнен! ⚙️\n\n" + str(
        await queue.build_queue_text()
    )
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(Command("show", "list", "sh", "ls"), F.from_user.id.in_(config.ADMINS))
async def adm_show(message: Message):
    """Отправляет список всех пользователей бота с их параметрами"""
    users = await get_all_users()

    if not users:
        text = "📋 Список пользователей пуст ⚙️"
        await message.answer(
            text=text,
            reply_markup=kb.admin.as_markup(resize_keyboard=True),
        )
        return

    def format_user(user: User) -> str:
        """Форматирует информацию о пользователе
        Добавляет строки только если соответствующие условия выполняются
        """
        user_info = ""
        user_info += f"🆔 ID: {user.id}"
        if user.name:
            user_info += f" 👤 {user.name}"
        if user.username:
            user_info += f" @{user.username}"
        user_info += " 🟢 хочет" if user.has_desire else " 🔴 не хочет"
        user_info += "\n"
        if not user.trusted:
            user_info += "⬆️ 🚫 Не доверенный 🚫 ⬆️"
        user_info += "\n"
        return user_info

    text = "📋 Список пользователей ⚙️\n"
    for user in users:
        text += format_user(user=user)

    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


# TODO: /rename, /change name, /change desire, /trust управление очередью админ панелью
# TODO: /notify, оповещения людей, когда очередь создается
