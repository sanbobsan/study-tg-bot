from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.qlogic import Queue
from bot.keyboards import keyboards as kb
from bot.data_base.dao import get_user

menu_router = Router()
queue = Queue()


# TODO: оформление бота
def get_queue_text() -> str:
    que, buf = queue.get_queue(), queue.get_buffer()

    queue_str = "Очередь:\n"
    for n, user in enumerate(que):
        username = ""
        if user.username is not None:
            username = f"@{user.username}"
        queue_str += f"{n + 1}. {user.name} {username}\n"

    buffer_str = "Буффер:\n"
    for user in buf:
        username = ""
        if user.username is not None:
            username = f"@{user.username}"
        buffer_str += f"{user.name} {username}\n"

    if len(que) == 0:
        queue_str += "0. Пусто\n"

    if len(buf) == 0:
        buffer_str += "Пусто\n"

    text = f"""{queue_str}
{buffer_str}
Буффер перемешивается и попадает в конец очереди
/join - присоединиться к буфферу
/leave - выйти из буффера"""
    return text


@menu_router.message(F.text, Command("menu"))
async def menu(message: Message):
    text = get_queue_text()
    await message.answer(
        text=text, reply_markup=kb.menu.as_markup(resize_keyboard=True)
    )


@menu_router.message(F.text, Command("join"))
async def join(message: Message):
    user = await get_user(message.from_user.id)
    queue.add_user(user)
    text = get_queue_text()
    await message.answer(
        text=text,
        reply_markup=kb.menu.as_markup(resize_keyboard=True),
    )


@menu_router.message(F.text, Command("leave"))
async def leave(message: Message):
    user = await get_user(message.from_user.id)
    queue.del_user(user)
    text = get_queue_text()
    await message.answer(
        text=text,
        reply_markup=kb.menu.as_markup(resize_keyboard=True),
    )


# TODO: отслеживание текущей очереди
# TODO: оповещения людей, когда очередь создается
# TODO: создать админ панель
@menu_router.message(F.text, Command("admshf"))
async def adm_shuffle(message: Message):
    queue.insert_buffer_in_queue()
    text = "admin\n" + get_queue_text()
    await message.answer(
        text=text,
        reply_markup=kb.menu.as_markup(resize_keyboard=True),
    )


@menu_router.message(F.text, Command("admclr"))
async def adm_clear(message: Message):
    queue.clear()
    text = "admin\n" + get_queue_text()
    await message.answer(
        text=text,
        reply_markup=kb.menu.as_markup(resize_keyboard=True),
    )
