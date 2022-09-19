from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


BUTTONS: list[types.KeyboardButton] = [
    types.KeyboardButton(text="about"),
    types.KeyboardButton(text="order"),
    types.KeyboardButton(text="order history"),
    types.KeyboardButton(text="help"),
]

PLACEHOLDER: str = "Select an action"


def get_single_row_keyboard(
    buttons: list[types.KeyboardButton] = BUTTONS,
    resize_keyboard: bool = True,
    input_field_placeholder: str = PLACEHOLDER,
) -> types.ReplyKeyboardMarkup:
    builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    builder.row(*buttons)
    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder=PLACEHOLDER
    )


def get_initial_keyboard() -> types.ReplyKeyboardMarkup:
    return get_single_row_keyboard(BUTTONS[:-1])


def get_post_about_keyboard() -> types.ReplyKeyboardMarkup:
    return get_single_row_keyboard(BUTTONS[1:])
