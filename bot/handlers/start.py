from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.data_base.dao import set_user
from bot.keyboards import keyboards as kb

start_router = Router()


@start_router.message(CommandStart())
async def echo(message: Message, state: FSMContext):
    await state.clear()
    user = await set_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        name=None,
    )
    if user is None or user.name is None:
        text = f"Ку, {message.from_user.username}! Используй /register"
        reply_markup = kb.start_register.as_markup()
    else:
        text = f"Ку, {user.name}! Используй /menu"
        reply_markup = kb.to_menu.as_markup()

    await message.answer(text=text, reply_markup=reply_markup)
