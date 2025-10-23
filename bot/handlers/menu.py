from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.qlogic import Queue
from bot.keyboards import keyboards as kb
from bot.data_base.dao import get_user

menu_router = Router()
queue = Queue()


def get_queue_text() -> str:
    queue_str = "Очередь\n"
    for n, user in enumerate(queue.get_queue()):
        queue_str += f"{n + 1}. {user.name}\n"

    buffer_str = "Буффер:\n"
    for user in queue.get_buffer():
        buffer_str += f"{user.name}\n"

    text = f"""{queue_str}
{buffer_str}

/join - присоединиться к буфферу в очередь
/leave - выйти из очереди и буффера

После попадания в буффер, ты попадешь в очередь, когда ее обновят
Буффер, перед тем как попасть в очередь мешается"""
    return text


@menu_router.message(F.text, Command("menu"))
async def menu(message: Message):
    text = get_queue_text()
    await message.answer(text=text, reply_markup=kb.menu.as_markup())


@menu_router.message(F.text, Command("join"))
async def join(message: Message):
    user = await get_user(message.from_user.id)
    queue.add_user(user)
    text = get_queue_text()
    await message.answer(text=text, reply_markup=kb.menu.as_markup())


@menu_router.message(F.text, Command("leave"))
async def leave(message: Message):
    user = await get_user(message.from_user.id)
    queue.del_user(user)
    text = get_queue_text()
    await message.answer(text=text, reply_markup=kb.menu.as_markup())


@menu_router.message(F.text, Command("admshf"))
async def adm_shuffle(message: Message):
    queue.insert_buffer_in_queue()
    text = "admin\n" + get_queue_text()
    await message.answer(text=text, reply_markup=kb.menu.as_markup())


@menu_router.message(F.text, Command("admclr"))
async def adm_clear(message: Message):
    queue.insert_buffer_in_queue()
    text = "admin\n" + get_queue_text()
    await message.answer(text=text, reply_markup=kb.menu.as_markup())
