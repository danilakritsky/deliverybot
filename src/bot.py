import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from dotenv import find_dotenv, load_dotenv

from replies import CommandReplies


logging.basicConfig(level=logging.INFO)

load_dotenv(dotenv_path=find_dotenv())

BOT_TOKEN: str | None = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise SystemExit("Bot token not provided!")

bot: Bot = Bot(token=BOT_TOKEN)
dp: Dispatcher = Dispatcher()


@dp.message(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(CommandReplies.START)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
