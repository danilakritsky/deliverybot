from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker, selectinload

from deliverybot.database import DB_PATH, MenuItem


async def get_async_session() -> AsyncSession:
    engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}", echo=True)
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_menu_sections() -> list[str]:
    # start session and CLOSE it automitcally upon exit from the context
    # manager
    async_session = await get_async_session()
    async with async_session() as session:
        # begin a transaction and COMMIT it automatically
        # if no exceptions were raised
        async with session.begin():
            return (
                (await session.execute(select(MenuItem.section).distinct()))
                .scalars()
                .all()
            )

async def get_section_items(
    section: str,
    session: AsyncSession
) -> list[dict]:
    # async with session:
    section_items = (
        await session.execute(
            select(MenuItem)
            .where(MenuItem.section == section)
            # https://stackoverflow.com/questions/70104873/how-to-access-relationships-with-async-sqlalchemy
            .options(selectinload(MenuItem.price))
        )
    ).scalars().all()
 
    return section_items
