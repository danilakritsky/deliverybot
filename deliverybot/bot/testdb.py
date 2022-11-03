import asyncio

from deliverybot.database.helpers import get_user_state

from deliverybot.database import (
    MenuItem,
    Order,
    OrderLine,
    UserState,
    async_session,
)


async def main():
    async with async_session() as session:
        await get_user_state(1, 1, 1, session)


if __name__ == '__main__':
    asyncio.run(main())
