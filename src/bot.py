import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import CONFIG
from replies import CommandReplies


logging.basicConfig(level=logging.INFO)

bot: Bot = Bot(token=CONFIG.BOT_TOKEN.get_secret_value(), parse_mode="HTML")

dp: Dispatcher = Dispatcher()


@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer(CommandReplies.START)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
