import asyncio
import logging

import routers
from aiogram import Bot, Dispatcher
from config import CONFIG
from middlewares import UpdatePrinterOuter


async def main():
    logging.basicConfig(level=logging.INFO)

    dp: Dispatcher = Dispatcher()
    dp.update.outer_middleware(UpdatePrinterOuter())
    dp.include_router(routers.info_router.router)
    dp.include_router(routers.order_router.router)

    bot: Bot = Bot(
        token=CONFIG.BOT_TOKEN.get_secret_value(), parse_mode="HTML"
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
