from aiogram.fsm.state import State, StatesGroup


class OrderState(StatesGroup):
    not_started = State()
    selecting_first_item = State()
    in_progress = State()
    reviewing = State()
