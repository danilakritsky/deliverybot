import asyncio

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from deliverybot.database import DB_PATH, MenuItem
from deliverybot.database.helpers import get_menu_sections


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


async def get_single_row_keyboard_inline(
    *buttons,
) -> types.InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    builder.row(*(BUTTONS[button] for button in buttons))
    return builder.as_markup(resize_keyboard=True)


async def get_initial_keyboard_inline() -> types.InlineKeyboardMarkup:
    return get_single_row_keyboard_inline("order", "order history", "about")


async def get_post_about_keyboard_inline() -> types.InlineKeyboardMarkup:
    return get_single_row_keyboard_inline("order", "order history", "help")


async def get_order_keyboard() -> types.InlineKeyboardMarkup:
    return get_single_row_keyboard_inline("order", "order history", "help")


async def get_menu_section_keyboard() -> types.InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    menu_sections: list[str] = await get_menu_sections()
    for button in menu_sections + [BUTTONS["cancel"]]:
        builder.add(button)
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)


if __name__ == "__main__":
    asyncio.run(get_menu_section_keyboard())
