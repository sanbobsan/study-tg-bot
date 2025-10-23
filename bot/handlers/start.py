from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.data_base.dao import set_user

start_router = Router()


@start_router.message(CommandStart())
async def echo(message: Message, state: FSMContext):
    await state.clear()
    user = await set_user(
        tg_id=message.from_user.id,
        username=message.from_user.username,
        name=None,
    )
    if user is None:
        text = f"Hi, {message.from_user.username}! You are new here"
    else:
        text = f"Hi, {user.name}!"

    await message.answer(text=text)
