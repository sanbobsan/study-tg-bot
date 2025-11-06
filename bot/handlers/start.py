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
        text = f"Привет, {message.from_user.full_name}! ✨\n\nДля начала нужно указать имя. Используй кнопку ниже или /name для этого"
        reply_markup = kb.start_register.as_markup(resize_keyboard=True)
    else:
        text = f"С возвращением, {user.name}! ✨\n\nИспользуй кнопку ниже или /menu, чтобы увидеть текущую очередь."
        reply_markup = kb.to_menu.as_markup(resize_keyboard=True)

    await message.answer(text=text, reply_markup=reply_markup)
