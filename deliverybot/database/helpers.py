from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, subqueryload
from sqlalchemy.sql.expression import Select

from deliverybot.database import (
    ItemPrice,
    MenuItem,
    Order,
    OrderLine,
    User,
    UserState,
)


async def run_select_stmt(stmt: Select, session: AsyncSession):
    results = (await session.execute(stmt)).scalars().all()
    match len(results):
        case 0:
            return None
        case 1:
            return results[0]
        case _:
            return results


async def get_menu_sections(session: AsyncSession) -> list[str]:
    stmt = select(MenuItem.section).distinct()
    return await run_select_stmt(stmt, session)


async def get_section_items(section: str, session: AsyncSession) -> list[dict]:
    stmt = (
        select(MenuItem).where(MenuItem.section == section)
        # https://stackoverflow.com/questions/70104873/how-to-access-relationships-with-async-sqlalchemy
        .options(selectinload(MenuItem.price))
    )
    return await run_select_stmt(stmt, session)


async def get_user_state(
    bot_id: int, chat_id: int, user_id: int, session: AsyncSession
) -> Order:
    print(bot_id, chat_id, user_id)
    stmt = (
        select(UserState)
        .options(
            selectinload(UserState.user), selectinload(UserState.current_order)
        )
        .where(User.bot_id == bot_id)
        .where(User.chat_id == chat_id)
        .where(User.user_id == user_id)
    )
    return await run_select_stmt(stmt, session)


async def get_user(
    bot_id: int, chat_id: int, user_id: int, session: AsyncSession
) -> Order:
    stmt = (
        select(User)
        .where(User.bot_id == bot_id)
        .where(User.chat_id == chat_id)
        .where(User.user_id == user_id)
    )
    return await run_select_stmt(stmt, session)


async def get_user_by_id(id: int, session: AsyncSession) -> Order:
    stmt = select(User).where(User.id == id)
    return await run_select_stmt(stmt, session)


async def get_user_state_by_id(id: int, session: AsyncSession) -> Order:
    stmt = (
        select(UserState)
        .where(UserState.id == id)
        .options(
            subqueryload(UserState.user),
            selectinload(UserState.current_order)
            .subqueryload(Order.order_lines)
            .subqueryload(OrderLine.item),
        )
        .options(
            subqueryload(UserState.current_order_line)
            .subqueryload(OrderLine.item)
            .subqueryload(MenuItem.price)
        )
    )
    return await run_select_stmt(stmt, session)


async def get_menu_item_by_id(id: int, session: AsyncSession) -> Order:
    stmt = (
        select(MenuItem)
        .where(MenuItem.id == id)
        .options(selectinload(MenuItem.price))
    )
    return await run_select_stmt(stmt, session)


async def get_order_by_id(id: int, session: AsyncSession) -> Order:
    stmt = (
        select(Order)
        .where(Order.id == id)
        .options(selectinload(Order.user), selectinload(Order.order_lines))
    )
    return await run_select_stmt(stmt, session)


async def get_order_line_by_id(id: int, session: AsyncSession) -> OrderLine:
    stmt = (
        select(OrderLine)
        .where(OrderLine.id == id)
        .options(selectinload(OrderLine.item))
    )
    return await run_select_stmt(stmt, session)


async def get_user_orders(user_id: int, session: AsyncSession) -> list[Order]:
    stmt = (
        select(Order)
        .where(Order.user_id == user_id)
        .options(selectinload(Order.order_lines))
    )
    orders = await run_select_stmt(stmt, session)
    if not isinstance(orders, list):
        return [orders]
    return orders
