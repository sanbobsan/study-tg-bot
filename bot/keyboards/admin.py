from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


admin = ReplyKeyboardBuilder()
admin.add(KeyboardButton(text="/shuffle"))
admin.add(KeyboardButton(text="/clear"))
admin.add(KeyboardButton(text="/menu"))
