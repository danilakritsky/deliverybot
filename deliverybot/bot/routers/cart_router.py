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


@router.chosen_inline_result(state=OrderState.not_started)
async def new_item_added(
    chosen_inline_result: types.ChosenInlineResult,
    state: FSMContext,
    bot: Bot,
):
    await state.set_state(OrderState.in_progress)
    data: dict[str, Any] = await state.get_data()
    async with async_session() as session:
        user_state: UserState = await get_user_state_by_id(data["id"], session)
        order_in_progress: Order = Order(user=user_state.user)
        session.add(order_in_progress)
        await session.commit()
        menu_item: MenuItem = await get_menu_item_by_id(
            chosen_inline_result.result_id, session
        )
        new_order_line: OrderLine = OrderLine(
            item=menu_item,
            quantity=1,
            price=menu_item.price.price,
            total=menu_item.price.price * 1,
            line_num=1,
        )
        session.add(new_order_line)
        await session.commit()
        new_order = await get_order_by_id(order_in_progress.id, session)
        new_order.order_lines.append(new_order_line)
        user_state.current_order = new_order
        user_state.current_order_line = new_order_line
        await session.commit()

        updated_message: types.Message | bool = await bot.edit_message_text(
            chat_id=user_state.user.chat_id,
            message_id=user_state.message_id,
            text=(
                f"{chosen_inline_result.result_id} has been added to the cart."
            ),
            reply_markup=await keyboards.inline.get_current_cart_keyboard(
                user_state
            ),
        )
    return updated_message


@router.callback_query(text="decrease", state=OrderState.in_progress)
async def decrease_item_quantity(
    callback: types.CallbackQuery, state: FSMContext
) -> types.Message | bool | None:
    edited_msg: types.Message | bool | None = None
    data: dict[str, Any] = await state.get_data()
    if callback.message:
        async with async_session() as session:
            user_state: UserState = await get_user_state_by_id(
                data["id"], session
            )
            qty: int = user_state.current_order_line.quantity

            if qty == 1:
                await callback.answer(
                    text="Can't decrease past 0.", show_alert=True
                )
            else:
                user_state.current_order_line.quantity += 1
                await session.commit()
                edited_msg = await callback.message.edit_text(
                    "ITEM DESCRIPTION",
                    reply_markup=await keyboards.inline.get_current_cart_keyboard(
                        user_state
                    ),
                )

    return edited_msg if edited_msg else callback.message
