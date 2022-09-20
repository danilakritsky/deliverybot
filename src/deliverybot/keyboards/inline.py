from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


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
