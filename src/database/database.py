# import asyncio

from pathlib import Path

from sqlalchemy import (
    create_engine,
    Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import (
    registry, declarative_base, relationship, selectinload, sessionmaker, Session
)


DB_PATH: Path = Path(__file__).parent / 'database.db'

mapper_registry = registry()
Base = mapper_registry.generate_base()


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    chat_id = Column(Integer)
    total = Column(Float)
    confirmed = Column(Boolean)
    date = Column(DateTime)
    review = Column(Text)
    stars = Column(Integer)
    items = relationship('OrderItem', back_populates='order')

    def __repr__(self):
        return (
            f'<Order id={self.id} user_id={self.user_id} chat_id={self.chat_id}>'
        )


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True)
    section = Column(String)
    name = Column(String)
    price = Column(Float)
    photo_id = Column(String)

    def __repr__(self):
        return f'<MenuItem section={self.section} name={self.name!r} price={self.price}>'


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer)
    # https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-one
    item = relationship('MenuItem')
    order = relationship('Order', back_populates='items')

    def __repr__(self):
        return f'<OrderItem order_id={self.order_id} item_id={self.item_id}>'


async def init_db():
    engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}", echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # expire_on_commit=False will prevent attributes from being expired
    # after commit.
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:
        async with session.begin():
            session.add_all(
                [
                    MenuItem(
                        section=section,
                        name=f'{section[:-1]} {num}',
                        price=num + 0.99,
                        photo_id=f'{section[:-1]}_{1:02d}.jpg'
                    )

                    for num in (1, 2, 3)
                    for section in ('meals', 'drinks', 'desserts')
                ]
            )
            stmt = select(MenuItem)
            result = await session.execute(stmt)
            
            for menu_item in result.scalars():
                print(menu_item)
        # sessions must be commited directly
        # since exiting the context manager simply closes it
        await session.commit()

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()

# asyncio.run(init_db())