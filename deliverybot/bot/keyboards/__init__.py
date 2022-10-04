import asyncio

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from deliverybot.database import UserState
from deliverybot.database.helpers import get_menu_sections


async def get_inline_button(
    name: str, user_state: UserState | None = None
) -> types.InlineKeyboardButton:
    match name:
        case "about":
            return types.InlineKeyboardButton(
                text="about", callback_data="about"
            )
        case "help":
            return types.InlineKeyboardButton(
                text="help", callback_data="help"
            )
        case "cancel":
            return types.InlineKeyboardButton(
                text="cancel", callback_data="cancel"
            )
        case "order_history":
            return types.InlineKeyboardButton(
                text="order history",
                switch_inline_query_current_chat="order_history",
            )
        case "order":
            return types.InlineKeyboardButton(
                text="order", callback_data="order"
            )
        case "decrease":
            return types.InlineKeyboardButton(
                text="-", callback_data="decrease"
            )
        case "increase":
            return types.InlineKeyboardButton(
                text="+", callback_data="increase"
            )
        case "previous_item":
            return types.InlineKeyboardButton(
                text="<-", callback_data="previous_item"
            )
        case "next_item":
            return types.InlineKeyboardButton(
                text="->", callback_data="next_item"
            )
        case "remove_item":
            return types.InlineKeyboardButton(
                text="x", callback_data="remove_item"
            )
        case "cancel_order":
            return types.InlineKeyboardButton(
                text="cancel", callback_data="cancel_order"
            )
        case "submit_order":
            return types.InlineKeyboardButton(
                text="submit", callback_data="submit_order"
            )
        case "add_another_item":
            return types.InlineKeyboardButton(
                text="add item", callback_data="add_another_item"
            )
        case "item_quantity":
            return types.InlineKeyboardButton(
                text=f"{user_state.current_order_line.quantity}",
                callback_data="item_quantity",
            )
        case "item_total":
            return types.InlineKeyboardButton(
                text=await format_float(
                    user_state.current_order_line.item.price.price
                    * user_state.current_order_line.quantity
                ),
                callback_data="item_total",
            )
        case "total_item_count":
            return types.InlineKeyboardButton(
                text=(
                    f"{user_state.current_order_line.line_num}"
                    " / "
                    f"{len(user_state.current_order.order_lines)}"
                ),
                callback_data="total_quantity",
            )
        case "total":
            return types.InlineKeyboardButton(
                text=await format_float(
                    sum(
                        line.total
                        for line in user_state.current_order.order_lines
                    )
                ),
                callback_data="total",
            )
        case _:
            pass


async def get_inline_buttons(
    buttons: list[types.InlineKeyboardButton],
    user_state: UserState | None = None,
) -> types.InlineKeyboardMarkup:
    return [await get_inline_button(button, user_state) for button in buttons]


async def build_inline_keyboard(
    buttons: list[types.InlineKeyboardButton],
    shape: tuple[int] | int | None = None,
) -> types.InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    print(buttons)
    builder.add(*buttons)
    if shape:
        if isinstance(shape, tuple):
            builder.adjust(*shape)
        elif isinstance(shape, int):
            builder.adjust(shape)
    return builder.as_markup()


async def format_float(float_num: float):
    return f"{float_num:.2f}"


async def get_menu_section_buttons(
    session: AsyncSession,
) -> types.InlineKeyboardMarkup:
    return [
        types.InlineKeyboardButton(
            text=section, switch_inline_query_current_chat=section
        )
        for section in await get_menu_sections(session)
    ]


async def get_cart_keyboard(
    user_state: UserState,
) -> types.InlineKeyboardMarkup:
    return await build_inline_keyboard(
        buttons=await get_inline_buttons(
            [
                "decrease",
                "item_quantity",
                "increase",
                "remove_item",
                "item_total",
                "add_another_item",
                "previous_item",
                "total_item_count",
                "next_item",
                "submit_order",
                "total",
                "cancel_order",
            ],
            user_state,
        ),
        shape=(3, 3, 3, 3),
    )
