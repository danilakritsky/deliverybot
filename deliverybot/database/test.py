import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from deliverybot.database import (
    MenuItem,
    Order,
    User,
    UserState,
    async_session,
)


async def get_user_state(bot_id: int, chat_id: int, user_id: int, session):
    stmt = (
        select(UserState)
        .options(selectinload(UserState.user))
        .where(User.bot_id == bot_id)
        .where(User.chat_id == chat_id)
        .where(User.user_id == user_id)
    )
    scalars = (await session.execute(stmt)).scalars()
    print(scalars.all())
    return scalars.one_or_none()


async def get():
    async with async_session() as session:
        return await get_user_state(1, 1, 1, session)


print(asyncio.run(get()))
