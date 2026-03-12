from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

from bot import keyboards as kb
from bot.db import User, create_user
from bot.utils.json_storage import load_bot_settings

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    trusted: bool = (await load_bot_settings())["trust_new"]
    if message.from_user is None:
        return
    user: User | None = await create_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        name=message.from_user.full_name,
        trusted=trusted,
    )
    if user is None or user.name is None:
        text: str = f"Привет, {message.from_user.full_name}! ✨\n\nДля начала нужно указать имя. Используй кнопку ниже или /name для этого"
        reply_markup: ReplyKeyboardMarkup = kb.start_register.as_markup(
            resize_keyboard=True
        )
    else:
        text = f"С возвращением, {user.name}! ✨\n\nИспользуй кнопку ниже или /menu, чтобы увидеть текущую очередь."
        reply_markup = kb.to_menu.as_markup(resize_keyboard=True)
    await message.answer(text=text, reply_markup=reply_markup)


@router.message(F.text, Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "💫 Этот бот помогает управлять очередью ожидания 💫\n"
        "Очередь строится из доверенных пользователей, у каждого из которых есть состояние желания. "
        "Люди, которые не хотят участвовать, пропускаются при сдвиге очереди.\n\n"
        "Доступные команды:\n"
        "- /start - начать работу с ботом\n"
        "- /help - показать помощь\n"
        "- /menu - показать текущую очередь\n"
        "- /name - изменить имя пользователя\n"
        "- /yes, /no - установить свое состояние желания\n"
    )
    await message.answer(text=text)
