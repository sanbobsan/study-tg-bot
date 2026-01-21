from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


admin = ReplyKeyboardBuilder()
admin.row(
    KeyboardButton(text="/next"),
    KeyboardButton(text="/menu"),
)