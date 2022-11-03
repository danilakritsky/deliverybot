from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from deliverybot.bot import keyboards
from deliverybot.bot.fsm.states import OrderState
from deliverybot.database import async_session
from deliverybot.database.helpers import get_message_text_by_placeholder


router: Router = Router()
# NOTE: Routers can only handle specific events
# to handle every update use dispatcher.update to register middleware


@router.message(Command(commands=["start"]))
async def start_cmd_issued(
    message: types.Message, state: FSMContext
) -> list[types.Message]:
    await state.clear()
    await state.set_state(OrderState.not_started)
    async with async_session() as session:
        result: list[types.Message] = [
            await message.answer(
                await get_message_text_by_placeholder("start", session)
            ),
            incoming_message := await message.answer(
                text=await get_message_text_by_placeholder("help", session),
                reply_markup=await keyboards.build_inline_keyboard(
                    await keyboards.get_inline_buttons(
                        ["order", "order_history", "about"]
                    )
                ),
            ),
        ]
        await state.update_data(message_id=incoming_message.message_id)
        # use return to return the outcoming message (to log it)
    return result


@router.callback_query(text="about")
async def show_about_info(
    callback: types.CallbackQuery, state: FSMContext
) -> types.Message | bool | None:
    edited_msg: types.Message | bool | None = None
    # https://stackoverflow.com/questions/51782177/mypy-item-of-union-has-no-attribute-error
    if callback.message:
        async with async_session() as session:
            edited_msg = await callback.message.edit_text(
                await get_message_text_by_placeholder("about", session),
                reply_markup=await keyboards.build_inline_keyboard(
                    await keyboards.get_inline_buttons(
                        ["order", "order_history", "help"]
                    )
                ),
            )
    await callback.answer()
    return edited_msg


@router.callback_query(text="help")
async def show_help(
    callback: types.CallbackQuery,
) -> types.Message | bool | None:
    edited_msg: types.Message | bool | None = None
    if callback.message:
        async with async_session() as session:
            edited_msg = await callback.message.edit_text(
                await get_message_text_by_placeholder("help", session),
                reply_markup=await keyboards.build_inline_keyboard(
                    await keyboards.get_inline_buttons(
                        ["order", "order_history", "about"]
                    )
                ),
            )
    await callback.answer()
    return edited_msg
