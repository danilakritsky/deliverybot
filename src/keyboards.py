from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


BUTTONS: list[types.KeyboardButton] = [
    types.KeyboardButton(text="about"),
    types.KeyboardButton(text="order"),
    types.KeyboardButton(text="order history"),
]

PLACEHOLDER: str = "Select an action"


def get_full_keyboard() -> types.ReplyKeyboardMarkup:
    builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    builder.row(*BUTTONS)
    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder=PLACEHOLDER
    )


def get_partial_keyboard() -> types.ReplyKeyboardMarkup:
    builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    builder.row(*BUTTONS[1:])
    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder=PLACEHOLDER
    )
