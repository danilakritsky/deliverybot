from aiogram.fsm.state import State, StatesGroup


class FSM(StatesGroup):
    _1_start_order = (
        State()
    )  # inline menus + | order | order history | about or help |
    _2_order_to_menus = (
        State()
    )  # inline items + | order | order history | about or help |
    _3_menu_to_cart = State()  # selected item + cart
    _3_1_cart_update = State()
    _3_2_cart_to_cancel_order = State()
    _3_3_cart_to_submit_order = State()
    _3_4_cart_to_help = State()
