from aiogram.fsm.state import StatesGroup, State


class WeatherFSM(StatesGroup):
    waiting_start_city = State()
    waiting_end_city = State()
    waiting_point = State()
    waiting_action = State()
    waiting_time = State()
