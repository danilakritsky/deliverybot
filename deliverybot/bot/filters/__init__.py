from aiogram.filters import BaseFilter
from aiogram.types import InlineQuery

from deliverybot.database.helpers import get_menu_sections
from deliverybot.database import async_session


class MenuSectionFilter(BaseFilter):
    async def __call__(self, inline_query: InlineQuery) -> bool:
        async with async_session() as session:
            return inline_query.query in await get_menu_sections(session)
