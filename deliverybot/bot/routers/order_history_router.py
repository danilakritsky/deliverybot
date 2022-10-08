import datetime
import logging
from typing import Any

from aiogram import Bot, Router, types
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


# @router.inline_query()
# async def catch_query(
#     inline_query: types.InlineQuery,
#     state: FSMContext,
# ) -> bool:
#     print(inline_query, '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


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

    return await inline_query.answer(
        results=results,
        is_personal=True,
        cache_time=0,  # NOTE: don't cache results to fetch newest orders
    )
