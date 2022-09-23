import logging
from typing import Any

from aiogram import Bot, Router, types
from aiogram.fsm.context import FSMContext
from magic_filter import F

from deliverybot.config import CONFIG
from deliverybot.bot import keyboards
from deliverybot.bot.fsm import FSM
from deliverybot.database.helpers import (
    get_menu_sections,
    get_section_items,
    get_async_session
)
from deliverybot.bot.filters import MenuSectionFilter

logging.basicConfig(level=logging.INFO)

router: Router = Router()


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
            "Choose a menu subsection:",
            reply_markup=await keyboards.inline.get_menu_section_keyboard(),
        )
    await callback.answer()
    return edited_msg


@router.inline_query(
    MenuSectionFilter(),
    state=FSM._1_start_order
)
async def select_menu_item(
    inline_query: types.InlineQuery,
    state: FSMContext,
) -> bool:
    async_session = await get_async_session()
    async with async_session() as session:
        results: list[types.InlineQueryResult] = []
        for menu_item in await get_section_items(inline_query.query, session):
            item = types.InlineQueryResultArticle(
                type="article",
                id=menu_item.id,
                title=f'{menu_item.name} price: {menu_item.price.price}',
                description=f'{menu_item.description}',
                input_message_content=types.InputTextMessageContent(
                    message_text=f"{menu_item.name} added to cart",
                    parse_mode="HTML"
                ),
                thumb_url=f'{CONFIG.SERVER_URI.get_secret_value()}/photos/{menu_item.photo_id}'
            )
            results.append(item)
            print(item.thumb_url)

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
