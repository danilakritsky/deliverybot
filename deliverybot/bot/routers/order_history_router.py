import datetime
import logging
from typing import Any

from aiogram import Bot, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

import deliverybot.database.helpers as helpers
from deliverybot.bot import keyboards
from deliverybot.bot.fsm.states import OrderState
from deliverybot.bot.replies import CommandReplies
from deliverybot.bot.routers.helpers import (
    make_item_description,
    make_order_summary,
)
from deliverybot.database import (
    MenuItem,
    Order,
    OrderLine,
    UserState,
    async_session,
)


logging.basicConfig(level=logging.INFO)

router: Router = Router()


@router.inline_query(
    lambda inline_query: inline_query.query == "order_history"
)
async def show_section_items_inline(
    inline_query: types.InlineQuery,
    state: FSMContext,
) -> bool:
    async with async_session() as session:
        results: list[types.InlineQueryResult] = []
        data = await state.get_data()

        user_state = await helpers.get_user_state_by_id(data["id"], session)
        orders = await helpers.get_user_orders(user_state.user_id, session)
        for order in orders:
            order = types.InlineQueryResultArticle(
                type="article",
                id=order.id,
                title=(
                    f"Date: {order.datetime:%Y-%m-%d %H:%M:%S}\n"
                    " - "
                    f"Total: {order.order_total}"
                ),
                description=await make_order_summary(
                    order, session, use_html=False
                ),
                input_message_content=types.InputTextMessageContent(
                    message_text=f"{order.id} selected",
                    parse_mode="HTML",
                ),
            )
            results.append(order)
    await state.set_state(OrderState.reviewing)
    return await inline_query.answer(
        results=results,
        is_personal=True,
        cache_time=0,  # NOTE: don't cache results to fetch newest orders
    )


@router.chosen_inline_result(state=OrderState.reviewing)
async def add_first_item(
    chosen_inline_result: types.ChosenInlineResult,
    state: FSMContext,
    bot: Bot,
):
    data: dict[str, Any] = await state.get_data()
    async with async_session() as session:
        user_state: UserState = await helpers.get_user_state_by_id(
            data["id"], session
        )
        order = await helpers.get_order_by_id(
            chosen_inline_result.result_id, session
        )
        user_state.current_order_id = order.id
        await session.commit()
        updated_message: types.Message | bool = await bot.edit_message_text(
            chat_id=user_state.user.chat_id,
            message_id=user_state.message_id,
            text=await make_order_summary(order, session),
            reply_markup=await keyboards.get_rating_keyboard(order),
        )
    return updated_message


@router.callback_query(
    lambda query: "rate" in query.data, state=OrderState.reviewing
)
async def rate_order(
    callback: types.Message, state: FSMContext
) -> list[types.Message]:
    if callback.message:
        data = await state.get_data()
        async with async_session() as session:
            user_state: UserState = await helpers.get_user_state_by_id(
                data["id"], session
            )
            order = await helpers.get_order_by_id(
                user_state.current_order_id, session
            )
            order.rating = callback.data[5]
            await session.commit()
            edited_msg = await callback.message.edit_text(
                text=await make_order_summary(
                    user_state.current_order, session
                ),
                reply_markup=await keyboards.get_rating_keyboard(order),
            )
        await callback.answer()

    return edited_msg if edited_msg else callback.message


@router.callback_query(text="clear_rating", state=OrderState.reviewing)
async def clear_rating(
    callback: types.Message, state: FSMContext
) -> list[types.Message]:
    if callback.message:
        data = await state.get_data()
        async with async_session() as session:
            user_state: UserState = await helpers.get_user_state_by_id(
                data["id"], session
            )
            order = await helpers.get_order_by_id(
                user_state.current_order_id, session
            )
            order.rating = None
            await session.commit()
            edited_msg = await callback.message.edit_text(
                text=await make_order_summary(
                    user_state.current_order, session
                ),
                reply_markup=await keyboards.get_rating_keyboard(order),
            )
        await callback.answer()

    return edited_msg if edited_msg else callback.message


@router.message(state=OrderState.reviewing)
async def post_review(
    message: types.Message, state: FSMContext, bot: Bot
) -> list[types.Message]:
    data = await state.get_data()
    async with async_session() as session:
        user_state: UserState = await helpers.get_user_state_by_id(
            data["id"], session
        )
        order = await helpers.get_order_by_id(
            user_state.current_order_id, session
        )
        order.review = message.text
        await session.commit()
        try:
            updated_message: types.Message | bool = (
                await bot.edit_message_text(
                    chat_id=user_state.user.chat_id,
                    message_id=user_state.message_id,
                    text=await make_order_summary(order, session),
                    reply_markup=await keyboards.get_rating_keyboard(order),
                )
            )
        except TelegramBadRequest:
            pass
        finally:
            await message.delete()
    return updated_message if updated_message else message
