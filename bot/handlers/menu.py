from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.data_base.dao import get_user
from bot.keyboards import keyboards as kb
from bot.qlogic import Queue

menu_router = Router()
queue = Queue()


# TODO: оформление бота
@menu_router.message(F.text, Command("menu"))
async def menu(message: Message):
    text = queue.get_text_for_message()
    await message.answer(
        text=text, reply_markup=kb.menu.as_markup(resize_keyboard=True)
    )


@menu_router.message(F.text, Command("join"))
async def join(message: Message):
    user = await get_user(message.from_user.id)
    queue.add_user_to_buffer(user)
    text = queue.get_text_for_message()
    await message.answer(
        text=text,
        reply_markup=kb.menu.as_markup(resize_keyboard=True),
    )


@menu_router.message(F.text, Command("leave"))
async def leave(message: Message):
    user = await get_user(message.from_user.id)
    queue.del_user_from_buffer(user)
    text = queue.get_text_for_message()
    await message.answer(
        text=text,
        reply_markup=kb.menu.as_markup(resize_keyboard=True),
    )
