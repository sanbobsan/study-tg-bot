from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.db.dao import update_user
from bot.keyboards import keyboards as kb

router = Router()


class Register(StatesGroup):
    entering_name = State()


@router.message(F.text, Command("register"))
async def register(message: Message, state: FSMContext):
    text = "Введи свое настоящее имя"
    await message.answer(text=text)
    await state.set_state(Register.entering_name)


@router.message(Register.entering_name, F.text)
async def name_enter(message: Message, state: FSMContext):
    await update_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        name=message.text,
    )
    text = "Имя записано, можешь использовать /menu"
    await message.answer(
        text=text,
        reply_markup=kb.to_menu.as_markup(resize_keyboard=True),
    )

    await state.clear()
