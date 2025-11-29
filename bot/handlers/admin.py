from typing import Protocol

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from bot.db.dao import BotSettingsDAO, get_all_users, update_user_by_id
from bot.filters.filter import IsAdmin
from bot.keyboards import admin as kb
from bot.utils.broadcaster import send_queue
from bot.utils.queue import QueueManager

queue_manager = QueueManager()

router = Router()
router.message.filter(IsAdmin())


@router.message(F.text, Command("admin", "adm"))
async def admin_panel(message: Message):
    """Панель администратора c доступными командами"""
    current = queue_manager.get_current_queue_name()
    text = (
        "⚙️ Панель администратора ⚙️\n"
        f"{current}\n"
        "Доступные команды:\n\n"
        "Управление очередями:\n"
        " • /create — создать очередь\n"
        " • /copy — копировать очередь\n"
        " • /delete — удалить очередь\n"
        " • /list, /ls — вывести список очередей\n"
        " • /current, /cur — изменить текущую очередь\n\n"
        "Управление определенной очередью:\n"
        " • /show, /sh — показать текущую очередь\n"
        " • /shuffle, /shf — перемешать очередь\n"
        " • /next, /nx  — перейти к следующему\n"
        " • /init — инициализировать очередь из бд\n"
        " • /update — обновить кешированный текст\n\n\n"
        "Управление пользователями:\n"
        " • /users — показать всех пользователей\n"
        " • /send_queue — отправить доверенным пользователям актуальную очередь\n"
        " • /rename <id> <new_name> — переименовывает пользователя\n"
        " • /have <id> <bool> — меняет желание пользователя на указанное\n"
        " • /trust <id> — сделать пользователя доверенным\n"
        " • /untrust <id> — не доверять пользователю (он не будет участвовать в очереди)\n\n"
        "Управление ботом:\n"
        " • /trust_new <bool> — изменяет настройку бота - доверять ли новым пользователям (обычно = 1, true)\n"
    )
    await message.answer(text=text)


# region Queues managment
@router.message(F.text, Command("create"))
async def create_queue(message: Message, command: CommandObject):
    """Создать очередь"""
    queue_name = command.args
    text = await queue_manager.create_queue(queue_name)
    await message.answer(text=text)


@router.message(F.text, Command("copy"))
async def copy_queue(message: Message, command: CommandObject):
    """Копировать очередь"""
    queue_name = command.args
    text = await queue_manager.copy_queue(queue_name)
    await message.answer(text=text)


@router.message(F.text, Command("delete"))
async def delete_queue(message: Message, command: CommandObject):
    """Удалить очередь"""
    queue_name = command.args
    text = queue_manager.delete_queue(queue_name=queue_name)
    await message.answer(text=text)


@router.message(F.text, Command("list", "ls"))
async def list_queues(message: Message):
    """Посмотреть все очереди"""
    text = queue_manager.get_queue_names()
    await message.answer(text)


@router.message(F.text, Command("current", "cur"))
async def set_current_queue(message: Message, command: CommandObject):
    """Установить текущую очередь"""
    queue_name = command.args
    text = await queue_manager.set_current_queue(queue_name=queue_name)
    await message.answer(text=text)


# endregion


# region Queue managment
@router.message(F.text, Command("show", "sh"))
async def queue_show(message: Message, command: CommandObject):
    """Возвращает текстовое представление очереди"""
    queue_name = command.args
    text = await queue_manager.queue_show(queue_name)
    await message.answer(text)


@router.message(F.text, Command("shuffle", "shf"))
async def queue_shuffle(message: Message, command: CommandObject):
    """Перемешивает очередь"""
    queue_name = command.args
    text = await queue_manager.queue_shuffle(queue_name)
    await message.answer(text)


@router.message(F.text, Command("next", "nx"))
async def queue_next_desiring(message: Message, command: CommandObject):
    """Переходит к следующему желающему в очереди"""
    queue_name = command.args
    text = await queue_manager.queue_next_desiring(queue_name)
    await message.answer(text)


@router.message(F.text, Command("init"))
async def queue_init(message: Message, command: CommandObject):
    """Инициализирует определенную очередь пользователями из бд"""
    queue_name = command.args
    text = await queue_manager.queue_init(queue_name)
    await message.answer(text)


@router.message(F.text, Command("save"))
async def save_queue(message: Message):
    """Сохраняет очереди в json файл"""
    await queue_manager.save_to_file()
    await message.answer("⚙️ Очереди сохранены")


# endregion


@router.message(F.text, Command("update"))
async def queue_update(message: Message, command: CommandObject):
    """Обновляет кешированный текст у определенной очереди"""
    queue_name = command.args
    text = await queue_manager.queue_update_cached_text(queue_name)
    await message.answer(text)


class User(Protocol):
    """Структурная типизация (утиная типизация)"""

    id: int
    name: str | None
    username: str | None
    has_desire: bool
    trusted: bool


# region Users manage trash
@router.message(Command("users"))
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


@router.message(Command("send_queue"))
async def adm_send_queue(message: Message):
    """Отправляет доверенным пользователям актуальную очередь"""
    await send_queue()
    text = "💬 Актуальная очередь отправлена доверенным пользователям ⚙️\n\n"
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(Command("rename"))
async def adm_rename(message: Message, command: CommandObject):
    """Переименовывает пользователя"""

    command_args = command.args.split() if command.args else []

    if not command_args or len(command_args) < 2:
        text = (
            "❌ Ошибка: не указан id или new_name пользователя ⚙️\n\n"
            "Использование: /rename <id> <new_name> (/show, чтобы получить id)\n"
            "Например: /rename 1 Иванов Иван"
        )
        await message.answer(
            text=text,
            reply_markup=kb.admin.as_markup(resize_keyboard=True),
            parse_mode=None,
        )
        return

    try:
        id, new_name = int(command_args[0]), " ".join(command_args[1:])
    except ValueError:
        text = (
            "❌ Ошибка: id указан неверно ⚙️\n\n"
            "Использование: /rename <id> <new_name> (/show, чтобы получить id)\n"
            "Например: /rename 1 Иванов Иван"
        )
        await message.answer(
            text=text,
            reply_markup=kb.admin.as_markup(resize_keyboard=True),
            parse_mode=None,
        )
        return

    user = await update_user_by_id(user_id=id, name=new_name)
    await queue_manager.queue_update_cached_text()

    text = f'👤 Результат ⚙️\nПользователь id={id} @{user.username} теперь "{new_name}"'
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(Command("have"))
async def adm_have(message: Message, command: CommandObject):
    """Меняет желание пользователя на указанное"""

    command_args = command.args.split() if command.args else []

    if not command_args or len(command_args) < 2:
        text = (
            "❌ Ошибка: не указан id или желание пользователя ⚙️\n\n"
            "Использование: /have <id> <bool> (1, 0 или true, false)\n"
            "Например: /have 1 true, /have 2 1"
        )
        await message.answer(
            text=text,
            reply_markup=kb.admin.as_markup(resize_keyboard=True),
            parse_mode=None,
        )
        return

    try:
        id, arg = int(command_args[0]), command_args[1]
    except ValueError:
        text = (
            "❌ Ошибка: id указан неверно ⚙️\n\n"
            "Использование: /have <id> <bool> (/show, чтобы получить id)\n"
            "Например: /have 1 true, /have 2 1"
        )
        await message.answer(
            text=text,
            reply_markup=kb.admin.as_markup(resize_keyboard=True),
            parse_mode=None,
        )
        return

    if arg.lower() in ["1", "true"]:
        new_desire = True
    elif arg.lower() in ["0", "false"]:
        new_desire = False
    else:
        text = (
            "❌ Ошибка: указан неверный аргумент ⚙️\n\n"
            "Использование: /have <id> <bool> (1, 0 или true, false)\n"
            "Например: /have 1 true, /have 2 1"
        )
        await message.answer(
            text=text,
            reply_markup=kb.admin.as_markup(resize_keyboard=True),
            parse_mode=None,
        )
        return

    user = await update_user_by_id(user_id=id, has_desire=new_desire)
    await queue_manager.queue_update_cached_text()

    text = f"👤 Результат ⚙️\nПользователь id={id} @{user.username} теперь {'не ' if not new_desire else ''}желает"
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(Command("trust"))
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
            await queue_manager.queue_update_cached_text()

            if updated_user is None:
                results.append(f"❌ Пользователь с id={user_id} не найден")
            else:
                name_info = f" {updated_user.name}" if updated_user.name else ""
                username_info = (
                    f" @{updated_user.username}" if updated_user.username else ""
                )
                results.append(
                    f"✅ Доверяем пользователю id={user_id}{name_info}{username_info}"
                )
        except ValueError:
            results.append(f'❌ "{arg}" не является числом')

    text = "🔒 Результат ⚙️\n\n" + "\n".join(results)
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(Command("untrust"))
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
            await queue_manager.queue_update_cached_text()

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


# region Bot managment
@router.message(Command("trust_new"))
async def adm_trust_new(message: Message, command: CommandObject):
    """Изменяет настройку бота - доверять ли новым пользователям"""

    command_args = command.args

    if not command_args:
        text = (
            "❌ Ошибка: не указан аргумент ⚙️\n\n"
            "Использование: /trust_new <bool> (1, 0) or (true, false)\n"
            "Например: /trust_new 1, /trust_new false"
        )
        await message.answer(
            text=text,
            reply_markup=kb.admin.as_markup(resize_keyboard=True),
            parse_mode=None,
        )
        return

    if command_args.lower() in ["1", "true"]:
        arg = True
    elif command_args.lower() in ["0", "false"]:
        arg = False
    else:
        text = (
            "❌ Ошибка: указан неверный аргумент ⚙️\n\n"
            "Использование: /trust_new <bool> (1, 0 или true, false)\n"
            "Например, /trust_new 1, /trust_new false"
        )
        await message.answer(
            text=text,
            reply_markup=kb.admin.as_markup(resize_keyboard=True),
            parse_mode=None,
        )
        return

    await BotSettingsDAO.set_bool_setting("trust_new", arg)

    text = f"🔒 Теперь бот {'не ' if not arg else ''}доверяет всем новым пользователям ⚙️\n\n"
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


# endregion
