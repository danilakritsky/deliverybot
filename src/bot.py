import asyncio
import logging

from aiogram import Bot, Dispatcher

import router
from config import CONFIG
from middlewares import UpdatePrinterOuter


async def main():
    logging.basicConfig(level=logging.INFO)

    dp: Dispatcher = Dispatcher()
    dp.update.outer_middleware(UpdatePrinterOuter())
    dp.include_router(router.router)

    bot: Bot = Bot(
        token=CONFIG.BOT_TOKEN.get_secret_value(), parse_mode="HTML"
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
