from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.db.dao import create_user
from bot.keyboards import keyboards as kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await create_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
    )

    if user is None or user.name is None:
        text = f"Ку, {message.from_user.username}! Используй /register"
        reply_markup = kb.start_register.as_markup(resize_keyboard=True)
    else:
        text = f"Ку, {user.name}! Используй /menu"
        reply_markup = kb.to_menu.as_markup(resize_keyboard=True)

    await message.answer(text=text, reply_markup=reply_markup)
