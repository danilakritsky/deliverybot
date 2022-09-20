from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


BUTTONS: list[types.InlineKeyboardButton] = [
    types.InlineKeyboardButton(text="about", callback_data="about"),
    types.InlineKeyboardButton(text="order", callback_data="order"),
    types.InlineKeyboardButton(
        text="order history", callback_data="order history"
    ),
    types.InlineKeyboardButton(text="help", callback_data="help"),
]


def get_single_row_keyboard_inline(
    buttons: list[types.InlineKeyboardButton] = BUTTONS,
    resize_keyboard: bool = True,
) -> types.InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    builder.row(*buttons)
    return builder.as_markup(resize_keyboard=True)


def get_initial_keyboard_inline():
    return get_single_row_keyboard_inline(BUTTONS[:-1])


def get_post_about_keyboard_inline():
    return get_single_row_keyboard_inline(BUTTONS[1:])


def get_order_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="food",
            # https://stackoverflow.com/questions/44737593/can-i-get-a-telegram-bot-to-put-some-text-into-the-users-message-input-box
            switch_inline_query_current_chat="food",  # to send inline queries
        ),
        types.InlineKeyboardButton(
            text="drinks", switch_inline_query_current_chat="drinks"
        ),
    )
    return builder.as_markup()
