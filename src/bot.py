import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Text
from aiogram.utils.keyboard import InlineKeyboardBuilder
from magic_filter import F

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


@dp.message(Command(commands=["orderstart"]))
@dp.message(Text(text=["order"]))
async def orderstart(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="food",
            # https://stackoverflow.com/questions/44737593/can-i-get-a-telegram-bot-to-put-some-text-into-the-users-message-input-box
            switch_inline_query_current_chat="food",  # to send inline queries
        ),
        types.InlineKeyboardButton(
            text="drinks", switch_inline_query_current_chat="drinks"
        ),
    )

    await message.answer(
        "Your cart is empty. Please select your first item:",
        reply_markup=builder.as_markup(),
    )


@dp.inline_query(F.query == "drinks")
async def send_random_value(inline_query: types.InlineQuery):
    results = [
        types.InlineQueryResultArticle(
            type="article",
            id=i,
            title=f"option {i}",
            input_message_content=types.InputTextMessageContent(
                message_text=i, parse_mode="HTML"
            ),
        )
        for i in range(3)
    ]
    # CallbackQuery must be answered
    # with a call to the asnwerCallbackQuery method
    # https://core.telegram.org/bots/api#callbackquery
    await inline_query.answer(results, is_personal=True)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
