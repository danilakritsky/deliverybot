from aiogram.utils.markdown import hide_link

from deliverybot.config import CONFIG
from deliverybot.database import MenuItem


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
