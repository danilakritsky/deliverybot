import logging
from typing import Any

from aiogram import Bot, Router, types
from aiogram.fsm.context import FSMContext
from magic_filter import F
from sqlalchemy import select

from deliverybot.bot import keyboards
from deliverybot.bot.filters import MenuSectionFilter
from deliverybot.bot.fsm.states import OrderState
from deliverybot.config import CONFIG
from deliverybot.database import (
    MenuItem,
    Order,
    OrderLine,
    UserState,
    async_session,
)
from deliverybot.database.helpers import (
    get_menu_item_by_id,
    get_order_by_id,
    get_section_items,
    get_user_by_id,
    get_user_state_by_id,
)


logging.basicConfig(level=logging.INFO)

router: Router = Router()


@router.callback_query(text="order")
async def open_menu(
    callback: types.CallbackQuery, state: FSMContext
) -> types.Message | bool | None:
    # NOTE: to collect the chosen results enable chosen_inline_result
    # via BotFather
    #  @ https://core.telegram.org/bots/inline#collecting-feedback
    # inline_query.answer expects results to be a list of ResuInlineQueryResult
    edited_msg: types.Message | bool | None = None
    if callback.message:
        if await state.get_state() == OrderState.not_started:
            async with async_session() as session:
                edited_msg = await callback.message.edit_text(
                    text="Choose a menu subsection:",
                    reply_markup=await keyboards.build_inline_keyboard(
                        (await keyboards.get_menu_section_buttons(session))
                        + (await keyboards.get_inline_buttons(["cancel"])),
                        shape=3,
                    ),
                )
        if state == OrderState.in_progress:
            pass

    # if callback.message:
    #     if state == OrderState.not_started:
    #         print('!!!!!!!!!!!!!!!!!!!!!')
    #         edited_msg = await callback.message.edit_text(
    #             CommandReplies.ABOUT,
    #             reply_markup=(
    #                 await keyboards.inline.get_post_about_keyboard_inline()
    #             ),
    #         )
    #     if state == OrderState.in_progress:
    #         print('!!!!!!!!!!!!!!')
    #         with async_session() as session:
    #             data = await state.get_data()
    #             user_state: UserState = await get_user_state_by_id(
    #                 data["id"], session
    #             )
    #             edited_msg = await callback.message.edit_text(
    #                 text=await make_item_description(
    #                     user_state.current_order_line.item
    #                 ),
    #                 reply_markup=await keyboards.inline.get_current_cart_keyboard(
    #                     user_state
    #                 )
    #             ) xds
    await callback.answer()
    return edited_msg


@router.inline_query(
    MenuSectionFilter(),
)
async def show_section_items_inline(
    inline_query: types.InlineQuery,
    state: FSMContext,
) -> bool:
    async with async_session() as session:
        results: list[types.InlineQueryResult] = []
        for menu_item in await get_section_items(inline_query.query, session):
            item = types.InlineQueryResultArticle(
                type="article",
                id=menu_item.id,
                title=f"{menu_item.name} price: {menu_item.price.price}",
                description=f"{menu_item.description}",
                input_message_content=types.InputTextMessageContent(
                    message_text=f"{menu_item.name} added to cart",
                    parse_mode="HTML",
                ),
                thumb_url=(
                    f"{CONFIG.SERVER_URI.get_secret_value()}"
                    f"/photos/{menu_item.photo_filename}"
                ),
            )
            results.append(item)

    return await inline_query.answer(results=results, is_personal=True)


@router.message(F.via_bot)
async def remove_reply_msg_to_chosen_inline_result(
    message: types.Message,
    bot: Bot,
    state: FSMContext,
) -> None:
    await bot.delete_message(message.chat.id, message.message_id)
