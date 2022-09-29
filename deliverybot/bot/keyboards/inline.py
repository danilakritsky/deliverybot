import asyncio

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from deliverybot.database import UserState
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
    return await get_single_row_keyboard_inline(
        "order", "order history", "about"
    )


async def get_post_about_keyboard_inline() -> types.InlineKeyboardMarkup:
    return await get_single_row_keyboard_inline(
        "order", "order history", "help"
    )


async def get_order_keyboard() -> types.InlineKeyboardMarkup:
    return await get_single_row_keyboard_inline(
        "order", "order history", "help"
    )


async def get_menu_section_keyboard(
    session: AsyncSession,
) -> types.InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    menu_sections: list[types.InlineKeyboardButton] = [
        types.InlineKeyboardButton(
            text=section, switch_inline_query_current_chat=section
        )
        for section in await get_menu_sections(session)
    ]

    for button in menu_sections + [BUTTONS["cancel"]]:
        builder.add(button)
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True)


async def get_current_cart_keyboard(
    user_state: UserState
) -> types.InlineKeyboardMarkup:

    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(text="+", callback_data="increase"),
        types.InlineKeyboardButton(
            text=f"{user_state.current_order_line.quantity}",
            callback_data="item_quantity"
        ),
        types.InlineKeyboardButton(text="-", callback_data="decrease"),

        types.InlineKeyboardButton(text="->", callback_data="next_item"),
        types.InlineKeyboardButton(
            text=f"{user_state.current_order_line.total}",
            callback_data="item_total"
        ),
        types.InlineKeyboardButton(text="<-", callback_data="previous_item"),

        types.InlineKeyboardButton(text="x", callback_data="remove"),

        types.InlineKeyboardButton(text=(
            f"{user_state.current_order_line.line_num}"
            " / "
            f"{len(user_state.current_order.order_lines)}"
            ),
            callback_data="total_quantity"
        ),
        types.InlineKeyboardButton(text=(
            f"{sum(line.total for line in user_state.current_order.order_lines)}"
            ),
            callback_data="total"
        ),

        BUTTONS["order"],
        types.InlineKeyboardButton(
            text="cancel", callback_data="cancel_order"
        ),
        types.InlineKeyboardButton(
            text="submit", callback_data="submit_order"
        ),
    )
    builder.adjust(3, 3, 3, 3)
    return builder.as_markup(resize_keyboard=True)

if __name__ == "__main__":
    asyncio.run(get_menu_section_keyboard())
