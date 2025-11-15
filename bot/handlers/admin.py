from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from bot.db.dao import BotSettingsDAO, get_all_users, update_user_by_id
from bot.db.models import User
from bot.filters.filter import IsAdmin
from bot.keyboards import admin as kb
from bot.utils.broadcaster import send_queue
from bot.utils.queue import Queue

router = Router()
router.message.filter(IsAdmin())
queue = Queue()


@router.message(Command("admin", "adm"))
async def admin_panel(message: Message):
    """Отправляет админ панелью с доступными командами"""
    text = (
        "⚙️ Панель администратора ⚙️\n"
        "Доступные команды:\n\n"
        "Управление очередью:\n"
        " • /create, /cr — создать очередь\n"
        " • /shuffle, /shf — перемешать очередь\n"
        " • /next — перейти к следующему\n\n"
        "Управление пользователями:\n"
        " • /show, /sh — показать всех пользователей\n"
        " • /send_queue — отправить доверенным пользователям актуальную очередь\n"
        " • /rename <id> <new_name> — переименовывает пользователя\n"
        " • /trust, /true <id> — сделать пользователя доверенным\n"
        " • /untrust <id> — не доверять пользователю (он не будет участвовать в очереди)\n\n"
        "Управление ботом:\n"
        " • /trust_new <bool> — изменяет настройку бота - доверять ли новым пользователям (обычно = 1, true)\n"
    )

    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
        parse_mode=None,
    )


# region Queue managment
@router.message(Command("create", "cr"))
async def adm_create(message: Message):
    """Создает очередь из существующих пользователей, отправляет отчет"""
    await queue.create_queue()
    text = "↩️ Очередь успешно создана! ⚙️\n\n" + str(await queue.build_queue_text())
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(Command("shuffle", "shf"))
async def adm_shuffle(message: Message):
    """Перемешивает существующую очередь, отправляет отчет"""
    queue.shuffle()
    text = "🔀 Очередь перемешана! ⚙️\n\n" + str(await queue.build_queue_text())
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


@router.message(Command("next"))
async def adm_next(message: Message):
    """Прокручивает очередь до следующего, отправляет отчет"""
    await queue.next_desiring()
    text = "➡️ Переход к следующему выполнен! ⚙️\n\n" + str(
        await queue.build_queue_text()
    )
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


# endregion


# region Users managment
@router.message(Command("show", "list", "sh", "ls"))
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

    text = f'👤 Результат ⚙️\nПользователь id={id} @{user.username} теперь "{new_name}"'
    await message.answer(
        text=text,
        reply_markup=kb.admin.as_markup(resize_keyboard=True),
    )


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


@router.message(Command("trust", "true"))
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
