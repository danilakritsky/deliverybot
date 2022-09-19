import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Text

from config import CONFIG
from keyboards import get_initial_keyboard, get_post_about_keyboard
from replies import CommandReplies


logging.basicConfig(level=logging.INFO)

bot: Bot = Bot(token=CONFIG.BOT_TOKEN.get_secret_value(), parse_mode="HTML")

dp: Dispatcher = Dispatcher()


@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message) -> None:
    await message.answer(CommandReplies.START)
    await message.answer(
        CommandReplies.HELP, reply_markup=get_initial_keyboard()
    )


@dp.message(Command(commands=["about"]))
@dp.message(Text(text=["about"]))
async def cmd_about(message: types.Message) -> None:
    await message.answer(
        CommandReplies.ABOUT, reply_markup=get_post_about_keyboard()
    )


@dp.message(Command(commands=["help"]))
@dp.message(Text(text=["help"]))
async def cmd_help(message: types.Message) -> None:
    await message.answer(
        CommandReplies.HELP, reply_markup=get_initial_keyboard()
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
