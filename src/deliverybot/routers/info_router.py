import keyboards
from aiogram import Router, types
from aiogram.filters import Command
from replies import CommandReplies


router: Router = Router()
# NOTE: Routers can only handle specific events
# to handle every update use dispatcher.update to register middleware


@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message) -> list[types.Message]:
    result: list[types.Message] = [
        await message.answer(CommandReplies.START),
        await message.answer(
            CommandReplies.HELP,
            reply_markup=keyboards.inline.get_initial_keyboard_inline(),
        ),
    ]
    # use return to return the outcoming message (to log it)
    return result


@router.callback_query(text="about")
async def about(callback: types.CallbackQuery) -> types.Message | bool | None:
    # https://stackoverflow.com/questions/51782177/mypy-item-of-union-has-no-attribute-error
    if callback.message:
        return await callback.message.edit_text(
            CommandReplies.ABOUT,
            reply_markup=keyboards.inline.get_post_about_keyboard_inline(),
        )
    return None


@router.callback_query(text="help")
async def help(callback: types.CallbackQuery) -> types.Message | bool | None:
    if callback.message:
        return await callback.message.edit_text(
            CommandReplies.HELP,
            reply_markup=keyboards.inline.get_initial_keyboard_inline(),
        )
    return None
