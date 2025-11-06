from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


admin = ReplyKeyboardBuilder()
admin.row(KeyboardButton(text="/next"), KeyboardButton(text="/menu"))
admin.row(KeyboardButton(text="/create"), KeyboardButton(text="/shuffle"))
