from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


BUTTONS: dict[str, types.InlineKeyboardButton] = {
    name: types.InlineKeyboardButton(text=name, callback_data=name)
    for name in ("about", "help", "order", "order history")
}


def get_single_row_keyboard_inline(*buttons) -> types.InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    builder.row(*(BUTTONS[button] for button in buttons))
    return builder.as_markup(resize_keyboard=True)


def get_initial_keyboard_inline():
    return get_single_row_keyboard_inline("order", "order history", "about")


def get_post_about_keyboard_inline():
    return get_single_row_keyboard_inline("order", "order history", "help")


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
