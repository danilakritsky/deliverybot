import json
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


# https://stackoverflow.com/questions/31085153/easiest-way-to-serialize-object-in-a-nested-dictionary
class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TelegramObject):
            return obj.__dict__
        else:
            return str(obj)


def print_json(obj) -> None:
    print(
        json.dumps(
            obj,
            indent=2,
            # will be used to convert non-serializable objects such as datetime
            # default=str,
            cls=Encoder,
        )
    )


class UpdatePrinterOuter(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> None:
        """
        Print every update as JSON.

        Parameters
        ----------
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]]
            Handler that processes the update (if any).
        event: TelegramOject
            Object representing the update's event (Message, InlineQuery, etc.)
            or the entire Update (if this class is used to handle every update
            by a Dispatcher).
        data: dict[str, Any]
            Aiogram-specific data pertaining to the update.
            If this middleware is registered with a Router
            to handle only a specific subset of events the entire Update
            will be available in data['event_update'].

        Returns
        -------
        None

        Notes
        -----
        The `data` and `event` params represent different entities
        depending on whether this class is used by Router
        (for a specific update event) or by Dispatcher to handle every update.
        """
        print_json(event)
        # print_json(data)
        # NOTE: handlers must return values for the outcoming messages
        # to be printed
        result = await handler(event, data)
        if isinstance(result, (list, tuple)):
            for item in result:
                print_json(item)
        else:
            print_json(result)
