from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


admin = ReplyKeyboardBuilder()
admin.row(
    KeyboardButton(text="/next"),
    KeyboardButton(text="/create"),
    KeyboardButton(text="/shuffle"),
)
admin.row(KeyboardButton(text="/show"), KeyboardButton(text="/send_queue"))
admin.row(KeyboardButton(text="/admin"), KeyboardButton(text="/menu"))
