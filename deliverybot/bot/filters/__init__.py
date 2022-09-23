from aiogram.filters import BaseFilter
from aiogram.types import InlineQuery

from deliverybot.database.helpers import get_menu_sections


class MenuSectionFilter(BaseFilter):
    async def __call__(self, inline_query: InlineQuery) -> bool:
        return inline_query.query in await get_menu_sections()
