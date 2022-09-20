from aiogram import Router
from aiogram import types as types


storage: dict
router: Router

async def cmd_start(message: types.Message) -> list[types.Message]: ...
async def cmd_about(message: types.Message) -> types.Message: ...
async def cmd_help(message: types.Message) -> types.Message: ...
