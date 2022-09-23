from typing import Any

from aiogram import Bot
from aiogram.fsm.storage.base import StorageKey, BaseStorage, StateType

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from deliverybot.database import Order, OrderItem
from deliverybot.database.helpers import get_async_session
from deliverybot.bot.fsm.states import state_to_str, OrderState


async def get_current_order(key: StorageKey, session: AsyncSession) -> Order:
    return await session.execute(
        select(Order)
        .where(Order.bot_id == key.bot_id)
        .where(Order.chat_id == key.chat_id)
        .where(Order.user_id == key.user_id)
        .where(Order.status != 'confirmed')
    ).scalars.one()


async def get_confirmed_orders(key: StorageKey, session: AsyncSession) -> list[Order]:
    return await session.execute(
        select(Order)
        .where(Order.bot_id == key.bot_id)
        .where(Order.chat_id == key.chat_id)
        .where(Order.user_id == key.user_id)
        .where(Order.status == 'confirmed')
    ).scalars.all()


class SQLiteStorage(BaseStorage):
    """
    SQLite database storage.
    """

    # TODO add __init__ to specify db path
    # StorageKey is a dataclass with the current bot_it, chat_id and user_id
    async def set_state(
        self, bot: Bot, key: StorageKey, state: StateType = None
    ) -> None:
        """
        Set state for specified key
        :param bot: instance of the current bot
        :param key: storage key
        :param state: new state
        """
        async_session: AsyncSession = get_async_session()

        state_str: str | None = (
            await state_to_str(state) if state is not None else None
        )
        async with async_session() as session:
            async with session.begin():
                if state == OrderState.start:
                    Order(
                        bot_id=key.bot_id,
                        chat_id=key.chat_id,
                        user_id=key.user_id,
                        state=state_str
                    )
                else:
                    order = await get_current_order(key, session)
                    if state is None:
                        await session.execute(
                            delete(Order).where(Order.id == order.id)
                        )
                    else:
                        order.state = state_str

    async def get_state(self, bot: Bot, key: StorageKey) -> str | None:
        """
        Get key state
        :param bot: instance of the current bot
        :param key: storage key
        :return: current state
        """
        async_session: AsyncSession = get_async_session()
        async with async_session() as session:
            order = await get_current_order(key, session)
            return order.state

    async def set_data(
        self, bot: Bot, key: StorageKey, data: dict[str, Any]
    ) -> None:
        """
        Write data (replace)
        :param bot: instance of the current bot
        :param key: storage key
        :param data: new data
        """
        async_session: AsyncSession = get_async_session()
        async with async_session() as session:
            order = await get_current_order(key, session)
            session.execute(
                update(Order)
                .where(Order.id == order.id)
                .values(**data)
            )

    async def get_data(self, bot: Bot, key: StorageKey) -> dict[str, Any]:
        """
        Get current data for key
        :param bot: instance of the current bot
        :param key: storage key
        :return: current data
        """
        async_session: AsyncSession = get_async_session()
        async with async_session() as session:
            return (await get_current_order(key, session)).__dict__

    async def update_data(
        self, bot: Bot, key: StorageKey, data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Update date in the storage for key (like dict.update)
        :param bot: instance of the current bot
        :param key: storage key
        :param data: partial data
        :return: new data
        """
        current_data = await self.get_data(bot=bot, key=key)
        current_data.update(data)
        await self.set_data(bot=bot, key=key, data=current_data)
        return current_data.copy()

    async def close(self) -> None:  # pragma: no cover
        """
        Close storage (database connection, file or etc.)
        """
        pass
