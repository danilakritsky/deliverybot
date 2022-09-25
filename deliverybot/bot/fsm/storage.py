from typing import Any

from aiogram import Bot
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey

from sqlalchemy import update

from deliverybot.database import (
    UserState, User, async_session
)
from deliverybot.database.helpers import get_user_state, get_user


class SQLiteStorage(BaseStorage):
    """
    SQLite database storage.
    """

    # TODO add __init__ to specify db path
    # StorageKey is a dataclass with the current bot_id, chat_id and user_id
    async def set_state(
        self, bot: Bot, key: StorageKey, state: StateType = None
    ) -> None:
        """
        Set state for specified key
        :param bot: instance of the current bot
        :param key: storage key
        :param state: new state
        """

        async with async_session() as session:
            async with session.begin():
                user_state = await get_user_state(
                    bot_id=key.bot_id,
                    chat_id=key.chat_id,
                    user_id=key.user_id,
                    session=session
                )
                user = await get_user(
                    bot_id=key.bot_id,
                    chat_id=key.chat_id,
                    user_id=key.user_id,
                    session=session
                )
                if not any([state, user_state, user]):
                    return
                if state is None:
                    await session.delete(user_state)
                    return
                if not user_state and not user:
                    # NOTE session.add shoud NOT be awaited
                    session.add(
                        UserState(
                            user=User(
                                bot_id=key.bot_id,
                                chat_id=key.chat_id,
                                user_id=key.user_id
                            ),
                            state=state.state,
                        )
                    )
                    return
                if not user_state and user:
                    session.add(
                        UserState(
                            user=user,
                            state=state.state,
                        )
                    )
                    return

    async def get_state(self, bot: Bot, key: StorageKey) -> str | None:
        """
        Get key state
        :param bot: instance of the current bot
        :param key: storage key
        :return: current state
        """
        async with async_session() as session:
            user_state = await get_user_state(
                    bot_id=key.bot_id,
                    chat_id=key.chat_id,
                    user_id=key.user_id,
                    session=session
                )
            return user_state.state if user_state else None

    async def set_data(
        self, bot: Bot, key: StorageKey, data: dict[str, Any]
    ) -> None:
        """
        Write data (replace)
        :param bot: instance of the current bot
        :param key: storage key
        :param data: new data
        """
        # do nothing if emtpy dict is passed by clear_data
        if not len(data):
            return

        async with async_session() as session:
            async with session.begin():
                user_state = await get_user_state(
                    bot_id=key.bot_id,
                    chat_id=key.chat_id,
                    user_id=key.user_id,
                    session=session
                )

                if not user_state.current_order or (
                    user_state.current_order.id != data['current_order'].id
                ):
                    user_state.current_order = data['current_order']

                if not user_state.user or (
                    user_state.user.id != data['user'].id
                ):
                    user_state.user = data['user']

                session.execute(
                    update(UserState)
                    .where(UserState.id == user_state.id)
                    .values(
                        **{
                            k: v for k, v in data.items()
                            if k not in (
                                '_sa_instance_state', 'current_order', 'user'
                            )
                        })
                )

    async def get_data(self, bot: Bot, key: StorageKey) -> dict[str, Any]:
        """
        Get current data for key
        :param bot: instance of the current bot
        :param key: storage key
        :return: current data
        """
        async with async_session() as session:
            return (
                await get_user_state(
                    bot_id=key.bot_id,
                    chat_id=key.chat_id,
                    user_id=key.user_id,
                    session=session
                )
            ).__dict__

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
