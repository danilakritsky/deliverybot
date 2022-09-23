import logging
from typing import Any

from aiogram import Bot, Router, types
from aiogram.fsm.context import FSMContext
from magic_filter import F

from deliverybot.bot import keyboards, routers
from deliverybot.bot.fsm import FSM


logging.basicConfig(level=logging.INFO)

router: Router = Router()

ORDERS: dict = {}


@router.callback_query(text="menu", state=FSM._1_start_order)
async def menu(
    callback: types.CallbackQuery, state: FSMContext
) -> types.Message | bool | None:
    # NOTE: to collect the chosen results enable chosen_inline_result
    # via BotFather
    #  @ https://core.telegram.org/bots/inline#collecting-feedback
    # inline_query.answer expects results to be a list of ResuInlineQueryResult
    edited_msg: types.Message | bool | None = None
    if callback.message:
        edited_msg = await callback.message.edit_text(
            "Choose a menu subscection",
            reply_markup=keyboards.inline.get_menu_section_keyboard(),
        )
    await callback.answer()
    return edited_msg


@router.inline_query(
    lambda inline_query: inline_query.query in MENU, state=FSM._1_start_order
)
async def select_menu_item(
    inline_query: types.InlineQuery,
    state: FSMContext,
) -> bool:
    results: list[types.InlineQueryResult] = [
        types.InlineQueryResultArticle(
            type="article",
            id=item,
            title=item,
            input_message_content=types.InputTextMessageContent(
                message_text=f"{item} added to cart", parse_mode="HTML"
            ),
        )
        for item in MENU[inline_query.query]
    ]
    return await inline_query.answer(results=results, is_personal=True)


@router.message(F.via_bot)
async def chosen_inline_result_message(
    message: types.Message,
    bot: Bot,
    state: FSMContext,
) -> None:
    await bot.delete_message(message.chat.id, message.message_id)


@router.chosen_inline_result()
async def menu_items(
    chosen_inline_result: types.ChosenInlineResult,
    state: FSMContext,
    bot: Bot,
):
    state_data: dict[str, Any] = await state.get_data()
    incoming_message: types.Message = state_data["incoming_message"]
    updated_message: types.Message | bool = await bot.edit_message_text(
        chat_id=incoming_message.chat.id,
        message_id=incoming_message.message_id,
        text=f"{chosen_inline_result.result_id} has bee added to the cart.",
    )
    return updated_message
