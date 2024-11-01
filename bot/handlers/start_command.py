from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

router = Router(name='start')


@router.message(F.text, Command('start'), StateFilter(None))
async def start_command_handler(message: Message):
    await message.answer('Привет, я предоставляю прогноз погоды по нескольким точкам маршрута\n'
                         'Для получения информации, используй команду /weather')
