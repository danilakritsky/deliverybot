from aiogram import Bot as Bot
from aiogram import Router, types


router: Router

async def orderstart(message: types.Message) -> types.Message: ...
async def select_drink(inline_query: types.InlineQuery) -> bool: ...
