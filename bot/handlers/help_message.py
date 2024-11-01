from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

router = Router(name='help')


@router.message(F.text, Command("help"), StateFilter(None))
async def cmd_help(message: Message):
    await message.answer(
        "Список доступных команд:\n"
        "/start - начать взаимодействие\n"
        "/help - получить список доступных команд\n"
        "/weather - получить прогноз погоды\n"
    )
