from aiogram.utils.markdown import hide_link

import deliverybot.database.helpers as helpers
from deliverybot.config import CONFIG
from deliverybot.database import MenuItem, OrderLine


async def make_item_description(menu_item: MenuItem) -> str:
    link: str = (
        f"{CONFIG.SERVER_URI.get_secret_value()}"
        f"/photos/{menu_item.photo_filename}"
    )
    return (
        f"{hide_link(link)}"
        f"<strong>{menu_item.name}</strong>\n"
        f"{menu_item.price.price}\n"
        f"{menu_item.description}"
    )


async def make_order_summary(order, session, use_html: bool = True) -> str:
    total: int = 0
    line: OrderLine
    summary: str = ""
    order = await helpers.get_order_by_id(order.id, session)
    for num, line in enumerate(order.order_lines, start=1):
        order_line: OrderLine = await helpers.get_order_line_by_id(
            line.id, session
        )
        line_description = (
            f"<strong><em>{order_line.item.name}</em></strong>\n"
            if use_html
            else f"{order_line.item.name} - "
        )
        summary += (
            line_description
            + f"{order_line.quantity} pcs."
            + (" | " if use_html else " - ")
            + f"{order_line.total}\n"
            + (
                "\n"
                if use_html
                else " | "
                if num < len(order.order_lines)
                else ""
            )
        )
        total += line.total
    newline = "\n"
    summary += f"<strong>Total: {total}.</strong>" if use_html else ""
    if order.rating:
        summary += (
            f"{newline if use_html else ' | '}" + f"{'★' * int(order.rating)}"
        )
    if order.review:
        summary += f"{newline if use_html else ' | '}" + f"{order.review}"
    return summary
