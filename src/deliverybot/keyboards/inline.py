from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from menu import MENU


BUTTONS: dict[str, types.InlineKeyboardButton] = {
    "about": types.InlineKeyboardButton(text="about", callback_data="about"),
    "help": types.InlineKeyboardButton(text="help", callback_data="help"),
    "cancel": types.InlineKeyboardButton(text="cancel", callback_data="help"),
    "order": types.InlineKeyboardButton(
        text="order",
        # can either specify inline_query or callback not both
        callback_data="menu",
    ),
    "order history": types.InlineKeyboardButton(
        text="order history", switch_inline_query_current_chat="order history"
    ),
}

section: str
MENU_SECTIONS: list[types.InlineKeyboardButton] = [
    types.InlineKeyboardButton(
        text=section, switch_inline_query_current_chat=section
    )
    for section in MENU
]


def get_single_row_keyboard_inline(*buttons) -> types.InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    builder.row(*(BUTTONS[button] for button in buttons))
    return builder.as_markup(resize_keyboard=True)


def get_initial_keyboard_inline() -> types.InlineKeyboardMarkup:
    return get_single_row_keyboard_inline("order", "order history", "about")


def get_post_about_keyboard_inline() -> types.InlineKeyboardMarkup:
    return get_single_row_keyboard_inline("order", "order history", "help")


def get_order_keyboard() -> types.InlineKeyboardMarkup:
    return get_single_row_keyboard_inline("order", "order history", "help")


def get_menu_section_keyboard() -> types.InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for button in MENU_SECTIONS + [BUTTONS["cancel"]]:
        builder.add(button)
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)
