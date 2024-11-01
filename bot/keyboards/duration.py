from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class DurationCallback(CallbackData, prefix="duration"):
    days: int


def duration_kbd() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='2 дня',
                                     callback_data=DurationCallback(days=2).pack()))

    builder.row(InlineKeyboardButton(text='3 дня',
                                     callback_data=DurationCallback(days=3).pack()))

    builder.row(InlineKeyboardButton(text='4 дня',
                                     callback_data=DurationCallback(days=4).pack()))

    builder.row(InlineKeyboardButton(text='5 дней',
                                     callback_data=DurationCallback(days=5).pack()))

    return builder
