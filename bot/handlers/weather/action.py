from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.filters.regex_match_filter import RegexMatchFilter
from bot.handlers.states.weather import WeatherFSM
from bot.keyboards.add_city import add_city_kbd
from entities.coords import LocationName
from entities.errors.api_error import APIAuthorizationError, APINumberOfRequests, APIError
from services.api.backend import Backend
from bot.keyboards.duration import duration_kbd

router = Router(name='weather_action')


@router.callback_query(WeatherFSM.waiting_action, F.data.startswith('add_city'))
async def add_city_handler(callback_query: CallbackQuery,
                           state: FSMContext):
    await callback_query.message.answer('Введи название города: ')
    await state.set_state(WeatherFSM.waiting_point)


@router.callback_query(WeatherFSM.waiting_action, F.data.startswith('time'))
async def time_chosen_handler(callback_query: CallbackQuery,
                              state: FSMContext):
    await state.set_state(WeatherFSM.waiting_time)
    await callback_query.message.answer('Выбери временной интервал прогноза: ',
                                        reply_markup=duration_kbd().as_markup())


@router.message(WeatherFSM.waiting_point,
                RegexMatchFilter(r"^[a-zA-Zа-яА-ЯёЁ\s'-]+$"))
async def city_chosen_handler(message: Message,
                              state: FSMContext,
                              backend: Backend):
    city = message.text
    data = await state.get_data()
    cities = data.get('cities', [])
    try:
        loc = backend.geolocation.get_location_key(LocationName(name=city))
        await state.update_data(cities=cities + [loc])

    except ConnectionError:
        await message.answer('Ошибка подключения к интернету. Попробуйте позже')
    except APIAuthorizationError:
        await message.answer('Ошибка авторизации у API (проверьте токен)')
    except APINumberOfRequests:
        await message.answer('Достигнут лимит по кол-ву токенов, необходимо оплатить API')
        await state.clear()
    except APIError:
        await message.answer('Невозможно найти место')
    except Exception as _:
        await message.answer('Где-то в коде ошибка')
    else:
        try:
            weather = backend.weather.get_weather(location=loc)
            await state.update_data({loc.key: weather})
        except APIAuthorizationError:
            await message.answer('Ошибка авторизации у API (проверьте токен)')
        except APINumberOfRequests:
            await message.answer('Достигнут лимит по кол-ву токенов, необходимо оплатить API')
        except APIError:
            await message.answer('Непредвиленная ошибка')
        except Exception as _:
            await message.answer('Где-то в коде ошибка')
        else:
            await state.set_state(WeatherFSM.waiting_action)
            await message.answer('Вы можете добавить промежуточные точки, нажатием кнопки \n'
                                 'добавить город ', reply_markup=add_city_kbd().as_markup())


@router.message(WeatherFSM.waiting_point)
async def end_chosen_invalid_handler(message: Message):
    await message.answer('Ошибка ввода города, попробуйте ещё раз: ')