from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.filters.regex_match_filter import RegexMatchFilter

from bot.handlers.states.weather import WeatherFSM
from bot.keyboards.add_city import add_city_kbd
from entities.coords import LocationName
from entities.errors.api_error import APIAuthorizationError, APINumberOfRequests, APIError
from services.api.backend import Backend

router = Router(name='weather_end_city')


@router.message(WeatherFSM.waiting_end_city,
                RegexMatchFilter(r"^[a-zA-Zа-яА-ЯёЁ\s'-]+$"))
async def end_chosen_handler(message: Message,
                             state: FSMContext,
                             backend: Backend):
    city = message.text
    try:
        loc = backend.geolocation.get_location_key(LocationName(name=city))
        await state.update_data(end_city=loc)

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


@router.message(WeatherFSM.waiting_end_city)
async def end_chosen_invalid_handler(message: Message):
    await message.answer('Ошибка ввода города, попробуйте ещё раз: ')
