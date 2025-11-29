from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.db.dao import update_user
from bot.keyboards import keyboards as kb
from bot.utils.queue import QueueManager

router = Router()
queue_manager = QueueManager()


class Register(StatesGroup):
    entering_name = State()


@router.message(F.text.lower() == "указать имя")
@router.message(Command("register", "name"))
async def register(message: Message, state: FSMContext):
    text = "Введи свое настоящее имя"
    await message.answer(text=text)
    await state.set_state(Register.entering_name)


@router.message(Register.entering_name, Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    text = "Изменение имени отменено"
    await message.answer(
        text=text,
        reply_markup=kb.to_menu.as_markup(resize_keyboard=True),
    )


@router.message(Register.entering_name, F.text)
async def enter_name(message: Message, state: FSMContext):
    await update_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        name=message.text,
    )
    await queue_manager.queue_update_cached_text()
    await state.clear()

    text = "✨ Отлично! Твоё имя сохранено\n\nИспользуй кнопку ниже или /menu, чтобы перейти в меню"
    await message.answer(
        text=text,
        reply_markup=kb.to_menu.as_markup(resize_keyboard=True),
    )
