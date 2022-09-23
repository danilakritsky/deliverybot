from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from deliverybot.database import DB_PATH, MenuItem


async def get_async_session() -> AsyncSession:
    engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}", echo=True)
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)()


async def get_menu_sections() -> list[str]:
    # start session and CLOSE it automitcally upon exit from the context
    # manager
    async with get_async_session() as session:
        # begin a transaction and COMMIT it automatically
        # if no exceptions were raised
        async with session.begin():
            return (
                await session.execute(select(MenuItem.section).distinct())
                .scalars()
                .all()
            )
