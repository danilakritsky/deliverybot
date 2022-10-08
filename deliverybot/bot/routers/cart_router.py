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


@router.chosen_inline_result(state=OrderState.not_started)
async def add_first_item(
    chosen_inline_result: types.ChosenInlineResult,
    state: FSMContext,
    bot: Bot,
):
    await state.set_state(OrderState.in_progress)
    data: dict[str, Any] = await state.get_data()
    async with async_session() as session:
        user_state: UserState = await helpers.get_user_state_by_id(
            data["id"], session
        )
        new_order: Order = Order(user=user_state.user)
        session.add(new_order)
        await session.commit()
        menu_item: MenuItem = await helpers.get_menu_item_by_id(
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
        new_order = await helpers.get_order_by_id(new_order.id, session)
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
            reply_markup=await keyboards.get_cart_keyboard(
                user_state,
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
        user_state: UserState = await helpers.get_user_state_by_id(
            data["id"], session
        )
        current_order = await helpers.get_order_by_id(
            user_state.current_order_id, session
        )
        menu_item: MenuItem = await helpers.get_menu_item_by_id(
            chosen_inline_result.result_id, session
        )

        new_order_line: OrderLine = OrderLine(
            item=menu_item,
            quantity=1,
            line_num=len(current_order.order_lines) + 1,
            price=menu_item.price.price,
            total=menu_item.price.price * 1,
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
            reply_markup=await keyboards.get_cart_keyboard(user_state),
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
            user_state: UserState = await helpers.get_user_state_by_id(
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
                    reply_markup=await keyboards.get_cart_keyboard(user_state),
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
            user_state: UserState = await helpers.get_user_state_by_id(
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
                reply_markup=await keyboards.get_cart_keyboard(user_state),
            )
            await callback.answer()

    return edited_msg if edited_msg else callback.message


@router.callback_query(text="next_item", state=OrderState.in_progress)
async def next_item(
    callback: types.CallbackQuery, state: FSMContext
) -> types.Message | bool | None:
    edited_msg: types.Message | bool | None = None
    data: dict[str, Any] = await state.get_data()
    if callback.message:
        async with async_session() as session:
            user_state: UserState = await helpers.get_user_state_by_id(
                data["id"], session
            )
            current_line_num: int = user_state.current_order_line.line_num
            current_lines: list[
                OrderLine
            ] = user_state.current_order.order_lines
            if current_line_num == max(
                line.line_num for line in current_lines
            ):
                await callback.answer(text="End of the cart!", show_alert=True)
            else:
                next_line: OrderLine = current_lines[current_line_num]
                user_state.current_order_line = next_line

                await session.commit()
                user_state = await helpers.get_user_state_by_id(
                    data["id"], session
                )
                edited_msg = await callback.message.edit_text(
                    text=await make_item_description(
                        user_state.current_order_line.item
                    ),
                    reply_markup=await keyboards.get_cart_keyboard(user_state),
                )
            await callback.answer()

    return edited_msg if edited_msg else callback.message


@router.callback_query(text="previous_item", state=OrderState.in_progress)
async def previous_item(
    callback: types.CallbackQuery, state: FSMContext
) -> types.Message | bool | None:
    edited_msg: types.Message | bool | None = None
    data: dict[str, Any] = await state.get_data()
    if callback.message:
        async with async_session() as session:
            user_state: UserState = await helpers.get_user_state_by_id(
                data["id"], session
            )
            current_line_num: int = user_state.current_order_line.line_num
            current_lines: list[
                OrderLine
            ] = user_state.current_order.order_lines
            if current_line_num == min(
                line.line_num for line in current_lines
            ):
                await callback.answer(text="End of the cart!", show_alert=True)
            else:
                next_line: OrderLine = current_lines[current_line_num - 2]
                user_state.current_order_line = next_line
                await session.commit()
                user_state = await helpers.get_user_state_by_id(
                    data["id"], session
                )
                edited_msg = await callback.message.edit_text(
                    text=await make_item_description(
                        user_state.current_order_line.item
                    ),
                    reply_markup=await keyboards.get_cart_keyboard(user_state),
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
            user_state: UserState = await helpers.get_user_state_by_id(
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
                current_line_num: int = user_state.current_order_line.line_num
                del user_state.current_order.order_lines[
                    user_state.current_order_line.line_num - 1
                ]
                await session.commit()
                user_state = await helpers.get_user_state_by_id(
                    data["id"], session
                )
                for num, line in enumerate(
                    user_state.current_order.order_lines, start=1
                ):
                    line.line_num = num
                await session.commit()
                user_state.current_order_line = (
                    user_state.current_order.order_lines[
                        0 if current_line_num == 1 else current_line_num - 2
                    ]
                )
                await session.commit()
                user_state = await helpers.get_user_state_by_id(
                    data["id"], session
                )
                edited_msg = await callback.message.edit_text(
                    text=await make_item_description(
                        user_state.current_order_line.item
                    ),
                    reply_markup=await keyboards.get_cart_keyboard(user_state),
                )
            await callback.answer()

        return edited_msg if edited_msg else callback.message


@router.callback_query(text="cancel_order")
@router.callback_query(text="cancel")
async def start_cmd_issued(
    callback: types.Message, state: FSMContext
) -> list[types.Message]:
    if callback.message:
        await state.clear()
        await state.set_state(OrderState.not_started)
        await state.update_data(message_id=callback.message.message_id)

        edited_msg = await callback.message.edit_text(
            text=CommandReplies.HELP,
            reply_markup=await keyboards.build_inline_keyboard(
                await keyboards.get_inline_buttons(
                    ["order", "order_history", "about"]
                )
            ),
        )
        await callback.answer()

    return edited_msg if edited_msg else callback.message


@router.callback_query(text="submit_order")
async def submit_order(
    callback: types.Message, state: FSMContext
) -> list[types.Message]:
    if callback.message:
        data = await state.get_data()
        async with async_session() as session:
            user_state: UserState = await helpers.get_user_state_by_id(
                data["id"], session
            )
            edited_msg = await callback.message.edit_text(
                text=await make_order_summary(
                    user_state.current_order, session
                ),
                reply_markup=await keyboards.build_inline_keyboard(
                    await keyboards.get_inline_buttons(
                        ["confirm_order", "back_to_cart"]
                    )
                ),
            )
        await callback.answer()

    return edited_msg if edited_msg else callback.message


@router.callback_query(text="confirm_order")
async def confirm_order(
    callback: types.Message, state: FSMContext
) -> list[types.Message]:
    if callback.message:
        data = await state.get_data()
        async with async_session() as session:
            user_state: UserState = await helpers.get_user_state_by_id(
                data["id"], session
            )
            user_state.current_order.datetime = datetime.datetime.now()
            user_state.current_order.order_total = sum(
                line.total for line in user_state.current_order.order_lines
            )
            await session.commit()
            user_state.current_order = None
            user_state.current_order_line = None
            await session.commit()
            await state.set_state(OrderState.not_started)

            edited_msg = await callback.message.edit_text(
                text="Thank you for ordering. Don't forget to leave a review!",
                reply_markup=await keyboards.build_inline_keyboard(
                    await keyboards.get_inline_buttons(
                        ["order", "order_history", "about"]
                    )
                ),
            )
        await callback.answer()

    return edited_msg if edited_msg else callback.message
