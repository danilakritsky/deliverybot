import asyncio
import logging

from aiogram import Bot, Dispatcher

# https://stackoverflow.com/questions/8899198/module-has-no-attribute
import deliverybot.bot.routers as routers
from deliverybot.bot.config import CONFIG
from deliverybot.bot.middlewares import UpdatePrinterOuter


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
