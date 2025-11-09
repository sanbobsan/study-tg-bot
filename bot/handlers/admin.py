from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from bot.db.dao import get_all_users, update_user_by_id
from bot.db.models import User
from bot.keyboards import admin as kb
from bot.utils.queue import Queue
from bot.utils.broadcaster import send_queue
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
        " • /create, /cr — создать очередь\n"
        " • /shuffle, /shf — перемешать очередь\n"
        " • /next — перейти к следующему\n"
        "Управление пользователями:\n"
        " • /show, /sh — показать всех пользователей\n"
        " • /send_queue — отправить доверенным пользователям актуальную очередь\n\n"
        " • /trust, /true <id> — сделать пользователя доверенным\n"
        " • /untrust <id> — не доверять полльзователю (он не будет участвовать в очереди)\n"
    )

    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
        parse_mode=None,
    )


# region Queue managment
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


# endregion


# region Users managment
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
        if not user.trusted:
            user_info += "\n⬆️ 🚫 Не доверенный 🚫 ⬆️"
        user_info += "\n"
        return user_info

    text = "📋 Список пользователей ⚙️\n"
    for user in users:
        text += format_user(user=user)

    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


# TODO: /send с возможностью писать от имени бота определенным пользователям
@router.message(Command("send_queue"), F.from_user.id.in_(config.ADMINS))
async def adm_send_queue(message: Message):
    """Отправляет доверенным пользователям актуальную очередь"""
    await send_queue()
    text = "💬 Актуальная очередь отправлена доверенным пользователям ⚙️\n\n"
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


# TODO: /trust и /untrust имеет очень схожую природу, объединить
@router.message(Command("trust", "true"), F.from_user.id.in_(config.ADMINS))
async def adm_trust(message: Message, command: CommandObject):
    """Делает пользователя доверенным по его id"""

    command_args = command.args.split() if command.args else []

    if not command_args:
        text = (
            "❌ Ошибка: не указан id пользователя ⚙️\n\n"
            "Использование: /trust <id> (/show, чтобы получить id)\n"
            "Можно указать несколько id: /trust 1 2 3"
        )
        await message.answer(
            text=text,
            reply_markup=kb.admin.as_markup(resize_keyboard=True),
            parse_mode=None,
        )
        return

    results = []
    for arg in command_args:
        try:
            user_id = int(arg)
            updated_user = await update_user_by_id(user_id=user_id, trusted=True)

            if updated_user is None:
                results.append(f"❌ Пользователь с id={user_id} не найден")
            else:
                name_info = f" {updated_user.name}" if updated_user.name else ""
                username_info = (
                    f" @{updated_user.username}" if updated_user.username else ""
                )
                results.append(
                    f"✅ Доверяем ользователю id={user_id}{name_info}{username_info}"
                )
        except ValueError:
            results.append(f'❌ "{arg}" не является числом')

    text = "🔒 Результат ⚙️\n\n" + "\n".join(results)
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(Command("untrust"), F.from_user.id.in_(config.ADMINS))
async def adm_untrust(message: Message, command: CommandObject):
    """Делает пользователя недоверенным по его id"""

    command_args = command.args.split() if command.args else []

    if not command_args:
        text = (
            "❌ Ошибка: не указан id пользователя ⚙️\n\n"
            "Использование: /untrust <id> (/show, чтобы получить id)\n"
            "Можно указать несколько id: /untrust 1 2 3"
        )
        await message.answer(
            text=text,
            reply_markup=kb.admin.as_markup(resize_keyboard=True),
            parse_mode=None,
        )
        return

    results = []
    for arg in command_args:
        try:
            user_id = int(arg)
            updated_user = await update_user_by_id(user_id=user_id, trusted=False)

            if updated_user is None:
                results.append(f"❌ Пользователь с id={user_id} не найден")
            else:
                name_info = f" {updated_user.name}" if updated_user.name else ""
                username_info = (
                    f" @{updated_user.username}" if updated_user.username else ""
                )
                results.append(
                    f"❎ Не доверяем пользователю id={user_id}{name_info}{username_info}"
                )
        except ValueError:
            results.append(f'❌ "{arg}" не является числом')

    text = "🔒 Результат ⚙️\n\n" + "\n".join(results)
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


# endregion

# TODO: /rename, /change name, /change desire управление очередью админ панелью
# TODO: /notify, оповещения людей, когда очередь создается
