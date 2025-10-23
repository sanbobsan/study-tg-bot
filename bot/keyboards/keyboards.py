from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


start_register = ReplyKeyboardBuilder()
start_register.add(KeyboardButton(text="/register"))

to_menu = ReplyKeyboardBuilder()
to_menu.add(KeyboardButton(text="/menu"))

menu = ReplyKeyboardBuilder()
menu.add(
    KeyboardButton(text="/join"),
    KeyboardButton(text="/leave"),
)
