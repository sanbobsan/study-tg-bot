from aiogram import F, Router
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.types import Message

router = Router()


# Этот хендлер будет реагировать на команду /base, когда не будет установлено состояние
@router.message(F.text, Command("base"), StateFilter(None))
async def base_easter_egg(message: Message, command: CommandObject):

    # Объект команды нужен, чтобы получать аргументы
    if command.args == "yes":
        text = "Тогда тебе надо сделать ее\\. Не знаешь как? \nВведи: `/base yes2`"
    elif command.args == "yes2":
        text = "Обратись ко мне"
    else:
        text = "Хочешь сделать собственную пасхалку? \nВведи: `/base yes`"

    # Для добавления форматирования: parse_mode
    await message.answer(text=text, parse_mode="MarkdownV2")
