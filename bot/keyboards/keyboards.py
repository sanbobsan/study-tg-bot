from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


start_register = ReplyKeyboardBuilder()
start_register.add(KeyboardButton(text="Указать имя"))

to_menu = ReplyKeyboardBuilder()
to_menu.add(KeyboardButton(text="Меню"))

menu = ReplyKeyboardBuilder()
menu.row(
    KeyboardButton(text="Хочу"),
    KeyboardButton(text="Не хочу"),
)
menu.add(KeyboardButton(text="Меню"))
