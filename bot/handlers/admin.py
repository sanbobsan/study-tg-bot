from typing import Sequence

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from bot.db.dao import get_all_users, update_user_by_id
from bot.db.models import User
from bot.filters.filter import IsAdmin
from bot.keyboards import admin as kb
from bot.utils.broadcaster import send_queue
from bot.utils.json_storage import save_bot_settings
from bot.utils.queue import QueueManager

queue_manager = QueueManager()

router = Router()
router.message.filter(IsAdmin())


@router.message(F.text, Command("admin", "adm"))
async def admin_panel(message: Message) -> None:
    """Панель администратора c доступными командами"""
    current: str = queue_manager.get_current_queue_name()
    text: str = (
        "⚙️ Панель администратора ⚙️\n"
        f"{current}\n"
        "Доступные команды:\n\n"
        "Управление очередями:\n"
        " • /create — создать очередь\n"
        " • /copy — копировать очередь\n"
        " • /delete — удалить очередь\n"
        " • /list, /ls — вывести список очередей\n"
        " • /current, /cur — изменить текущую очередь\n"
        " • /save — сохранить очереди в файл\n\n"
        "Управление определенной очередью:\n"
        " • /show, /sh — показать текущую очередь\n"
        " • /shuffle, /shf — перемешать очередь\n"
        " • /next, /nx  — перейти к следующему\n"
        " • /forward, /fwd <steps> — сдвинуть очередь вперед на заданное количество шагов (по умолчанию = 1)\n"
        " • /backward, /bwd <steps> — сдвинуть очередь назад на заданное количество шагов (по умолчанию = 1)\n"
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
    await message.answer(
        text=text, reply_markup=kb.admin.as_markup(resize_keyboard=True)
    )


# region Queues management
@router.message(F.text, Command("create"))
async def create_queue(message: Message, command: CommandObject) -> None:
    """Создать очередь"""
    queue_name: str | None = command.args
    text: str = await queue_manager.create_queue(queue_name)
    await message.answer(text=text)


@router.message(F.text, Command("copy"))
async def copy_queue(message: Message, command: CommandObject) -> None:
    """Копировать очередь"""
    queue_name: str | None = command.args
    text: str = await queue_manager.copy_queue(queue_name)
    await message.answer(text=text)


@router.message(F.text, Command("delete"))
async def delete_queue(message: Message, command: CommandObject) -> None:
    """Удалить очередь"""
    queue_name: str | None = command.args
    text: str = queue_manager.delete_queue(queue_name=queue_name)
    await message.answer(text=text)


@router.message(F.text, Command("list", "ls"))
async def list_queues(message: Message) -> None:
    """Посмотреть все очереди"""
    text: str = queue_manager.get_queue_names()
    await message.answer(text)


@router.message(F.text, Command("current", "cur"))
async def set_current_queue(message: Message, command: CommandObject) -> None:
    """Установить текущую очередь"""
    queue_name: str | None = command.args
    text: str = await queue_manager.set_current_queue(queue_name=queue_name)
    await message.answer(text=text)


@router.message(F.text, Command("save"))
async def save_queue(message: Message) -> None:
    """Сохраняет очереди в json файл"""
    await queue_manager.save_to_file()
    await message.answer("⚙️ Очереди сохранены")


# endregion


# region Queue management
@router.message(F.text, Command("show", "sh"))
async def queue_show(message: Message, command: CommandObject) -> None:
    """Возвращает текстовое представление очереди"""
    queue_name: str | None = command.args
    text: str = await queue_manager.queue_show(queue_name)
    await message.answer(text)


@router.message(F.text, Command("shuffle", "shf"))
async def queue_shuffle(message: Message, command: CommandObject) -> None:
    """Перемешивает очередь"""
    queue_name: str | None = command.args
    text: str = await queue_manager.queue_shuffle(queue_name)
    await message.answer(text)


@router.message(F.text, Command("next", "nx"))
async def queue_next_desiring(message: Message, command: CommandObject) -> None:
    """Переходит к следующему желающему в очереди"""
    queue_name: str | None = command.args
    text: str = await queue_manager.queue_next_desiring(queue_name)
    await message.answer(text)


@router.message(F.text, Command("forward", "fwd", "backward", "bwd"))
async def queue_move(message: Message, command: CommandObject) -> None:
    """Циклический сдвиг очереди вперед или назад на заданное количество шагов"""
    command_args: list[str] = command.args.split() if command.args else []
    try:
        steps: int = int(command_args[0]) if command_args else 1
    except ValueError:
        await message.answer("❌ Ошибка: количество шагов указано неверно")
        return
    queue_name: str | None = command_args[1] if len(command_args) > 1 else None
    if command.command in ["backward", "bwd"]:
        steps = -steps

    text: str = await queue_manager.queue_move(queue_name=queue_name, steps=steps)
    await message.answer(text=text)


@router.message(F.text, Command("init"))
async def queue_init(message: Message, command: CommandObject) -> None:
    """Инициализирует определенную очередь пользователями из бд"""
    queue_name: str | None = command.args
    text: str = await queue_manager.queue_init(queue_name)
    await message.answer(text)


@router.message(F.text, Command("update"))
async def queue_update(message: Message, command: CommandObject) -> None:
    """Обновляет кешированный текст у определенной очереди"""
    queue_name: str | None = command.args
    text: str = await queue_manager.queue_update_cached_text(queue_name)
    await message.answer(text)


# endregion


# region Users management


@router.message(F.text, Command("users"))
async def users(message: Message) -> None:
    """Отправляет список всех пользователей бота с их параметрами"""
    users: Sequence[User] = await get_all_users()

    if not users:
        text = "📋 Список пользователей пуст ⚙️"
        await message.answer(text=text)
        return

    def format_user(user: User) -> str:
        """Форматирует информацию о пользователе
        Добавляет строки только если соответствующие условия выполняются
        """
        user_info: str = ""
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

    await message.answer(text=text)


@router.message(F.text, Command("send_queue"))
async def send_queue_cmd(message: Message) -> None:
    """Отправляет доверенным пользователям актуальную очередь"""
    await send_queue()
    text = "💬 Актуальная очередь отправлена доверенным пользователям ⚙️\n\n"
    await message.answer(text=text)


async def validate_and_update_user(user_id_arg: str, **kwds) -> str:
    """Проверяет аргументы и обновляет пользователя в бд"""
    try:
        user_id: int = int(user_id_arg)
    except ValueError:
        return "❌ Ошибка: id указан неверно"

    user: User | None = await update_user_by_id(user_id=user_id, **kwds)

    if user is None:
        return "❌ Ошибка: пользователь с таким id не найден"

    await queue_manager.queue_update_cached_text()
    return f"✅ Пользователь {user.name} обновлен"


def validate_bool_arg(arg: str) -> bool | None:
    """Проверяет аргумент на булево значение"""
    if arg.lower() in ["1", "true", "yes", "y", "да"]:
        return True
    elif arg.lower() in ["0", "false", "no", "n", "нет"]:
        return False
    else:
        return None


@router.message(F.text, Command("rename"))
async def rename(message: Message, command: CommandObject) -> None:
    """Переименовывает пользователя"""

    command_args: list[str] = command.args.split() if command.args else []

    if not command_args or len(command_args) < 2:
        await message.answer(
            text="❌ Ошибка: не указан id или new_name пользователя ⚙️\n\n"
            "Использование: /rename <id> <new_name> (/show, чтобы получить id)\n"
            "Например: /rename 1 Иванов Иван"
        )
        return

    text: str = await validate_and_update_user(
        command_args[0], name=" ".join(command_args[1:])
    )
    await message.answer(text=text)


@router.message(Command("have"))
async def have(message: Message, command: CommandObject) -> None:
    """Меняет желание пользователя на указанное"""

    command_args: list[str] = command.args.split() if command.args else []

    if not command_args or len(command_args) < 2:
        text = (
            "❌ Ошибка: не указан id или желание пользователя ⚙️\n\n"
            "Использование: /have <id> <bool> (1, 0 или true, false)\n"
            "Например: /have 1 true, /have 2 1"
        )
        await message.answer(text=text)
        return

    bool_value: None | bool = validate_bool_arg(command_args[1])
    if bool_value is None:
        text = (
            "❌ Ошибка: указан неверный аргумент желания ⚙️\n\n"
            "Использование: /have <id> <bool> (1, 0 или true, false)\n"
            "Например: /have 1 true, /have 2 1"
        )
        await message.answer(text=text)
        return

    text = await validate_and_update_user(command_args[0], has_desire=bool_value)
    await message.answer(text=text)


@router.message(Command("trust", "untrust"))
async def trust(message: Message, command: CommandObject) -> None:
    """Делает пользователя доверенным по его id"""

    command_args: list[str] = command.args.split() if command.args else []

    if not command_args:
        text = (
            "❌ Ошибка: не указан id пользователя ⚙️\n\n"
            "Использование: /trust <id> (/show, чтобы получить id)\n"
            "Можно указать несколько id: /trust 1 2 3, /untrust 4 5 6"
        )
        await message.answer(
            text=text,
            parse_mode=None,
        )
        return

    if command.command == "trust":
        trusted = True
    else:
        trusted = False

    results = []
    for arg in command_args:
        try:
            user_id = int(arg)
            updated_user = await update_user_by_id(user_id=user_id, trusted=trusted)
            await queue_manager.queue_update_cached_text()

            if updated_user is None:
                results.append(f"❌ Пользователь с id={user_id} не найден")
            else:
                name_info = f" {updated_user.name}" if updated_user.name else ""
                username_info = (
                    f" @{updated_user.username}" if updated_user.username else ""
                )
                results.append(
                    "✅ Доверяем пользователю id="
                    if trusted
                    else "❎ Не доверяем пользователю id="
                    + f"{user_id}{name_info}{username_info}"
                )
        except ValueError:
            results.append(f'❌ "{arg}" не является числом')

    text = "🔒 Результат ⚙️\n\n" + "\n".join(results)
    await message.answer(text=text)


# endregion


# region Bot managment
@router.message(Command("trust_new"))
async def adm_trust_new(message: Message, command: CommandObject):
    """Изменяет настройку бота - доверять ли новым пользователям"""

    command_args: str | None = command.args

    if not command_args:
        text = (
            "❌ Ошибка: не указан аргумент ⚙️\n\n"
            "Использование: /trust_new <bool> (1, 0) or (true, false)\n"
            "Например: /trust_new 1, /trust_new false"
        )
        await message.answer(
            text=text,
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
            parse_mode=None,
        )
        return

    await save_bot_settings({"trust_new": arg})

    text = f"🔒 Теперь бот {'не ' if not arg else ''}доверяет всем новым пользователям ⚙️\n\n"
    await message.answer(
        text=text,
    )


# endregion
