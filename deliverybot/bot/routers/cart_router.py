import logging
from typing import Any

from aiogram import Bot, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hide_link
from magic_filter import F
from sqlalchemy import select

from deliverybot.bot import keyboards
from deliverybot.bot.filters import MenuSectionFilter
from deliverybot.bot.fsm.states import OrderState
from deliverybot.bot.routers.helpers import make_item_description
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
async def add_first_item(
    chosen_inline_result: types.ChosenInlineResult,
    state: FSMContext,
    bot: Bot,
):
    await state.set_state(OrderState.in_progress)
    data: dict[str, Any] = await state.get_data()
    async with async_session() as session:
        user_state: UserState = await get_user_state_by_id(data["id"], session)
        new_order: Order = Order(user=user_state.user)
        session.add(new_order)
        await session.commit()
        menu_item: MenuItem = await get_menu_item_by_id(
            chosen_inline_result.result_id, session
        )
        new_order_line: OrderLine = OrderLine(
            item=menu_item,
            quantity=1,
            line_num=1,
            price=menu_item.price.price,
            total=menu_item.price.price * 1,
        )
        session.add(new_order_line)
        await session.commit()
        new_order = await get_order_by_id(new_order.id, session)
        new_order.order_lines.append(new_order_line)
        user_state.current_order = new_order
        user_state.current_order_line = new_order_line
        await session.commit()
        updated_message: types.Message | bool = await bot.edit_message_text(
            chat_id=user_state.user.chat_id,
            message_id=user_state.message_id,
            text=await make_item_description(
                user_state.current_order_line.item
            ),
            reply_markup=await keyboards.build_inline_keyboard(
                buttons=await keyboards.get_inline_buttons(
                    [
                        "decrease",
                        "item_quantity",
                        "increase",
                        "remove_item",
                        "item_total",
                        "add_another_item",
                        "previous_item",
                        "total_item_count",
                        "next_item",
                        "submit_order",
                        "total",
                        "cancel_order",
                    ],
                    user_state,
                ),
                shape=(3, 3, 3, 3),
            ),
        )
    return updated_message


@router.chosen_inline_result(state=OrderState.in_progress)
async def add_another_item(
    chosen_inline_result: types.ChosenInlineResult,
    state: FSMContext,
    bot: Bot,
):
    data: dict[str, Any] = await state.get_data()
    async with async_session() as session:
        user_state: UserState = await get_user_state_by_id(data["id"], session)
        # new_order: Order = Order(user=user_state.user)
        # session.add(new_order)
        # await session.commit()
        current_order = await get_order_by_id(
            user_state.current_order_id, session
        )
        menu_item: MenuItem = await get_menu_item_by_id(
            chosen_inline_result.result_id, session
        )
        new_order_line: OrderLine = OrderLine(
            item=menu_item,
            quantity=1,
            line_num=len(current_order.order_lines) + 1,
        )
        session.add(new_order_line)
        await session.commit()
        current_order.order_lines.append(new_order_line)
        user_state.current_order_line = new_order_line
        await session.commit()
        updated_message: types.Message | bool = await bot.edit_message_text(
            chat_id=user_state.user.chat_id,
            message_id=user_state.message_id,
            text=await make_item_description(
                user_state.current_order_line.item
            ),
            reply_markup=await keyboards.build_inline_keyboard(
                buttons=await keyboards.get_inline_buttons(
                    [
                        "decrease",
                        "item_quantity",
                        "increase",
                        "remove_item",
                        "item_total",
                        "add_another_item",
                        "previous_item",
                        "total_item_count",
                        "next_item",
                        "submit_order",
                        "total",
                        "cancel_order",
                    ],
                    user_state,
                ),
                shape=(3, 3, 3, 3),
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
                # update price if it has changed
                user_state.current_order_line.price = (
                    user_state.current_order_line.item.price.price
                )
                user_state.current_order_line.quantity -= 1
                user_state.current_order_line.total = (
                    user_state.current_order_line.price
                    * user_state.current_order_line.quantity
                )
                await session.commit()
                edited_msg = await callback.message.edit_text(
                    text=await make_item_description(
                        user_state.current_order_line.item
                    ),
                    reply_markup=await keyboards.build_inline_keyboard(
                        buttons=await keyboards.get_inline_buttons(
                            [
                                "decrease",
                                "item_quantity",
                                "increase",
                                "remove_item",
                                "item_total",
                                "add_another_item",
                                "previous_item",
                                "total_item_count",
                                "next_item",
                                "submit_order",
                                "total",
                                "cancel_order",
                            ],
                            user_state,
                        ),
                        shape=(3, 3, 3, 3),
                    ),
                )
                await callback.answer()

    return edited_msg if edited_msg else callback.message


@router.callback_query(text="increase", state=OrderState.in_progress)
async def increase_item_quantity(
    callback: types.CallbackQuery, state: FSMContext
) -> types.Message | bool | None:
    edited_msg: types.Message | bool | None = None
    data: dict[str, Any] = await state.get_data()
    if callback.message:
        async with async_session() as session:
            user_state: UserState = await get_user_state_by_id(
                data["id"], session
            )
            user_state.current_order_line.price = (
                user_state.current_order_line.item.price.price
            )
            user_state.current_order_line.quantity += 1
            user_state.current_order_line.total = (
                user_state.current_order_line.price
                * user_state.current_order_line.quantity
            )
            await session.commit()

            edited_msg = await callback.message.edit_text(
                text=await make_item_description(
                    user_state.current_order_line.item
                ),
                reply_markup=await keyboards.build_inline_keyboard(
                    buttons=await keyboards.get_inline_buttons(
                        [
                            "decrease",
                            "item_quantity",
                            "increase",
                            "remove_item",
                            "item_total",
                            "add_another_item",
                            "previous_item",
                            "total_item_count",
                            "next_item",
                            "submit_order",
                            "total",
                            "cancel_order",
                        ],
                        user_state,
                    ),
                    shape=(3, 3, 3, 3),
                ),
            )
            await callback.answer()

    return edited_msg if edited_msg else callback.message


@router.callback_query(text="remove_item", state=OrderState.in_progress)
async def remove_item(
    callback: types.CallbackQuery, state: FSMContext
) -> types.Message | bool | None:
    edited_msg: types.Message | bool | None = None
    data: dict[str, Any] = await state.get_data()
    if callback.message:
        async with async_session() as session:
            user_state: UserState = await get_user_state_by_id(
                data["id"], session
            )
            if len(user_state.current_order.order_lines) == 1:
                message_id: int = user_state.message_id
                await state.clear()
                await state.set_state(OrderState.not_started)
                await state.update_data(message_id=message_id)
                edited_msg = await callback.message.edit_text(
                    text="Cart is empty, please select an item:",
                    reply_markup=await keyboards.build_inline_keyboard(
                        (await keyboards.get_menu_section_buttons(session))
                        + (await keyboards.get_inline_buttons(["cancel"])),
                        shape=3,
                    ),
                )
            else:
                # TODO
                user_state.current_order_line.line_num
                edited_msg = await callback.message.edit_text(
                    text=await make_item_description(
                        user_state.current_order_line.item
                    ),
                    reply_markup=await keyboards.build_inline_keyboard(
                        buttons=await keyboards.get_inline_buttons(
                            [
                                "decrease",
                                "item_quantity",
                                "increase",
                                "remove_item",
                                "item_total",
                                "add_another_item",
                                "previous_item",
                                "total_item_count",
                                "next_item",
                                "submit_order",
                                "total",
                                "cancel_order",
                            ],
                            user_state,
                        ),
                        shape=(3, 3, 3, 3),
                    ),
                )
            await callback.answer()

        return edited_msg if edited_msg else callback.message
