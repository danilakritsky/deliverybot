from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import registry, relationship, sessionmaker

from deliverybot.config import CONFIG


engine = create_async_engine(
    f"sqlite+aiosqlite:///{CONFIG.DB_PATH}", echo=True
)

# expire_on_commit=False will prevent attributes from being expired
# after commit.
async_session: AsyncSession = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

mapper_registry = registry()
Base = mapper_registry.generate_base()


class UserState(Base):
    __tablename__ = "user_states"

    id = Column(Integer, primary_key=True)

    state = Column(Text)
    message_id = Column(Integer)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", uselist=False)

    current_order_id = Column(Integer, ForeignKey("orders.id"))
    current_order = relationship(
        "Order",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )

    current_order_line_id = Column(Integer, ForeignKey("order_lines.id"))
    current_order_line = relationship(
        "OrderLine", uselist=False, single_parent=True
    )


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("bot_id", "chat_id", "user_id"),)

    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer)
    chat_id = Column(Integer)
    user_id = Column(Integer)
    phone_number = Column(Text)

    orders = relationship("Order", back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)

    datetime = Column(DateTime)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="orders", uselist=False)

    review = Column(Text)
    stars = Column(Integer)

    order_total = Column(Float)

    order_lines = relationship("OrderLine", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order id={self.id} user_id={self.user_id}>"


class OrderLine(Base):
    __tablename__ = "order_lines"

    id = Column(Integer, primary_key=True)

    order_id = Column(Integer, ForeignKey("orders.id"))
    line_num = Column(Integer)
    item_id = Column(Integer, ForeignKey("menu_items.id"))
    item = relationship("MenuItem")

    quantity = Column(Integer)
    price = Column(Float)
    total = Column(Float)

    def __repr__(self):
        return f"<OrderItem order_id={self.order_id} item_id={self.item_id}>"


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True)
    section = Column(String)
    name = Column(String)
    photo_filename = Column(String)
    description = Column(String)
    price = relationship("ItemPrice", uselist=False)

    def __repr__(self):
        return f"<MenuItem section={self.section} name={self.name!r}>"


class ItemPrice(Base):
    __tablename__ = "item_prices"

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("menu_items.id"))
    price = Column(Float)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
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
                        photo_filename=f"{name.replace(' ', '_')}.jpg",
                        description=f"This is the description of {name}.",
                    )
                    for num in (1, 2, 3)
                    for section in ("meals", "drinks", "desserts")
                ]
            )

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    # await engine.dispose()
