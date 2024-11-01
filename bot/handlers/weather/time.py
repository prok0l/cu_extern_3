from asyncio import sleep

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.states.weather import WeatherFSM
from bot.keyboards.duration import DurationCallback
from bot.entities.weather_view import WeatherView

router = Router(name='weather_duration')


@router.callback_query(WeatherFSM.waiting_time, DurationCallback.filter())
async def duration_handler(callback_query: CallbackQuery,
                           callback_data: DurationCallback,
                           state: FSMContext):
    await callback_query.answer()

    selected_days = callback_data.days
    data = await state.get_data()
    cities = [data.get('start_city')] + data.get('cities', []) + [data.get('end_city')]
    view = WeatherView(cities=cities, data=data, duration=selected_days)
    for msg in view.as_view():
        await callback_query.message.answer(msg, parse_mode="Markdown")
        await sleep(0.5)

    await state.clear()

