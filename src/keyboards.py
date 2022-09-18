from aiogram import types


def get_full_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard: list[list[types.KeyboardButton]] = [
        [
            types.KeyboardButton(text="about"),
            types.KeyboardButton(text="order"),
            types.KeyboardButton(text="order history"),
        ]
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Select an action",  # TODO: use constants
    )


def get_partial_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard: list[list[types.KeyboardButton]] = [
        [
            types.KeyboardButton(text="order"),
            types.KeyboardButton(text="order history"),
        ]
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Select an action",  # TODO: use constants
    )
