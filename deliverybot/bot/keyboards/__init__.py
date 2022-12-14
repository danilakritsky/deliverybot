from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from deliverybot.database import Order, UserState
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
                text="➖", callback_data="decrease"
            )
        case "increase":
            return types.InlineKeyboardButton(
                text="➕", callback_data="increase"
            )
        case "previous_item":
            return types.InlineKeyboardButton(
                text="⬅️", callback_data="previous_item"
            )
        case "next_item":
            return types.InlineKeyboardButton(
                text="➡️", callback_data="next_item"
            )
        case "remove_item":
            return types.InlineKeyboardButton(
                text="❌", callback_data="remove_item"
            )
        case "cancel_order":
            return types.InlineKeyboardButton(
                text="cancel order", callback_data="cancel_order"
            )
        case "back":
            return types.InlineKeyboardButton(
                text="back", callback_data="back"
            )
        case "submit_order":
            return types.InlineKeyboardButton(
                text="submit order", callback_data="submit_order"
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
        case "back_to_cart":
            return types.InlineKeyboardButton(
                text="back to cart",
                callback_data="back_to_cart",
            )
        case "confirm_order":
            return types.InlineKeyboardButton(
                text="confirm order",
                callback_data="confirm_order",
            )
        case "clear_rating":
            return types.InlineKeyboardButton(
                text="clear rating",
                callback_data="clear_rating",
            )
        case "clear_review":
            return types.InlineKeyboardButton(
                text="clear review",
                callback_data="clear_review",
            )
        case "add_review":
            return types.InlineKeyboardButton(
                text=(
                    "📩 send a message below to\n"
                    "add/modify a review for this order"
                ),
                callback_data="add_review",
            )
        case _:
            pass


async def get_inline_buttons(
    buttons: list[str],
    user_state: UserState | None = None,
) -> list[types.InlineKeyboardButton]:
    return [await get_inline_button(button, user_state) for button in buttons]


async def build_inline_keyboard(
    buttons: list[types.InlineKeyboardButton],
    shape: tuple[int, ...] | int | None = None,
) -> types.InlineKeyboardMarkup:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
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
) -> list[types.InlineKeyboardButton]:
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


async def get_rating_keyboard(order: Order) -> types.InlineKeyboardMarkup:
    rating: int = int(order.rating) if order.rating else 0
    buttons: list[types.InlineKeyboardButton] = []
    if rating:
        for i in range(1, rating + 1):
            buttons.append(
                types.InlineKeyboardButton(
                    text="⭐",
                    callback_data=f"rate_{i}_stars",
                )
            )
    for i in range(rating + 1, 6):
        buttons.append(
            types.InlineKeyboardButton(
                text="☆",
                callback_data=f"rate_{i}_stars",
            )
        )
    return await build_inline_keyboard(
        buttons=(
            buttons
            + [await get_inline_button("add_review")]
            + [await get_inline_button("clear_rating")]
            + [await get_inline_button("clear_review")]
            + [await get_inline_button("back")]
        ),
        shape=(5, 1, 2, 1),
    )
