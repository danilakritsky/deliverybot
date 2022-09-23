import asyncio
from pathlib import Path

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import registry, relationship, sessionmaker


DB_PATH: Path = Path(__file__).parent / "database.db"

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
    items = relationship("OrderItem", back_populates="order")

    def __repr__(self):
        return (
            "<Order"
            f" id={self.id} user_id={self.user_id} chat_id={self.chat_id}>"
        )


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True)
    section = Column(String)
    name = Column(String)
    price = Column(Float)
    photo_id = Column(String)  # TODO: rename to file
    description = Column(String)
    price = relationship("ItemPrice", uselist=False)

    def __repr__(self):
        return (
            "<MenuItem"
            f" section={self.section} name={self.name!r}>"
        )

class ItemPrice(Base):
    __tablename__ = "item_prices"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('menu_items.id'))
    price = Column(Float)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer)
    # https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-one
    item = relationship("MenuItem")
    order = relationship("Order", back_populates="items")

    def __repr__(self):
        return f"<OrderItem order_id={self.order_id} item_id={self.item_id}>"


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
    # start session and CLOSE it automitcally upon exit from the context
    # manager
    async with async_session() as session:
        # begin a transaction and COMMIT it automatically
        # if no exceptions were raised
        async with session.begin():
            session.add_all(
                [
                    MenuItem(
                        section=section,
                        name=(name := f"{section[:-1]} {num:02d}"),
                        # https://stackoverflow.com/questions/16151729/attributeerror-int-object-has-no-attribute-sa-instance-state
                        price=ItemPrice(price=num + 0.99),
                        photo_id=f"{name.replace(' ', '_')}.jpg",
                        description=f'This is the description of {name}.'
                    )
                    for num in (1, 2, 3)
                    for section in ("meals", "drinks", "desserts")
                ]
            )

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
