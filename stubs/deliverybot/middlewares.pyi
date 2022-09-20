import json
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class Encoder(json.JSONEncoder):
    def default(self, obj): ...

def print_json(obj) -> None: ...

class UpdatePrinterOuter(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> None: ...
