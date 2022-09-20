from aiogram import Router, types
from aiogram.filters import Command, Text
from keyboards.regular import get_initial_keyboard, get_post_about_keyboard
from replies import CommandReplies


storage = {}

router: Router = Router()
# NOTE: Routers can only handle specific events
# to handle every update use dispatcher.update to register middleware


@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message) -> types.Message:
    result: list[types.Message] = [
        await message.answer(CommandReplies.START),
        await message.answer(
            CommandReplies.HELP, reply_markup=get_initial_keyboard()
        ),
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
