from aiogram import Router, types
from aiogram.filters import Command, Text
from aiogram.utils.keyboard import InlineKeyboardBuilder
from magic_filter import F

from keyboards import get_initial_keyboard, get_post_about_keyboard
from replies import CommandReplies


router: Router = Router()
# NOTE: Routers can only handle specific events
# to handle every update use dispatcher.update to register middleware


@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message) -> types.Message:
    result: list[types.Message] = [
        await message.answer(CommandReplies.START),
        await message.answer(
            CommandReplies.HELP, reply_markup=get_initial_keyboard()
        )
    ]
    # use return to return the outcoming message (to log it)
    return result


@router.message(Command(commands=["about"]))
@router.message(Text(text=["about"]))
async def cmd_about(message: types.Message) -> types.Message:
    return await message.answer(
        CommandReplies.ABOUT, reply_markup=get_post_about_keyboard()
    )


@router.message(Command(commands=["help"]))
@router.message(Text(text=["help"]))
async def cmd_help(message: types.Message) -> types.Message:
    return await message.answer(
        CommandReplies.HELP, reply_markup=get_initial_keyboard()
    )


@router.message(Command(commands=["orderstart"]))
@router.message(Text(text=["order"]))
async def orderstart(message: types.Message) -> types.Message:
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

    return await message.answer(
        "Your cart is empty. Please select your first item:",
        reply_markup=builder.as_markup(),
    )


@router.inline_query(F.query == "drinks")
async def send_random_value(inline_query: types.InlineQuery) -> bool:
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
    return await inline_query.answer(results, is_personal=True)
