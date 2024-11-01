from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def add_city_kbd() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='Добавить город',
                                     callback_data='add_city'))

    builder.row(InlineKeyboardButton(text='Получить прогноз',
                                     callback_data='time'))

    return builder
