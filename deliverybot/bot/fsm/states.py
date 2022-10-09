from aiogram.fsm.state import State, StatesGroup


class OrderState(StatesGroup):
    not_started = State()
    in_progress = State()
    reviewing = State()


async def state_to_str(state: State) -> str:
    return state.state[(state.state.find(":") + 1) :]
