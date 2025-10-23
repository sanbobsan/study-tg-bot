from aiogram import F, Router
from aiogram.types import Message

router = Router()


@router.message(F.text)
async def echo(message: Message):
    await message.answer(message.text)
