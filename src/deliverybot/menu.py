from aiogram import types


MENU: dict = {
    "meals": ["meal 1", "meal 2", "meal 3"],
    "drinks": ["drink 1", "drink 2", "drink 3"],
    "desserts": ["dessert 1", "dessert 2", "dessert 3"],
}

MENU_SECTIONS_KEYBOARD: list[types.InlineQueryResult] = [
    types.InlineQueryResultArticle(
        type="article",
        id=menu_section,
        title=f"{menu_section}",
        input_message_content=types.InputTextMessageContent(
            message_text=f"Selecting {menu_section}",
            parse_mode="HTML",
        ),
    )
    for menu_section in MENU
]
