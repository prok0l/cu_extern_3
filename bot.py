import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.middlewares.throttling import ThrottlingMiddleware
from config import Config, load_config
from services.api.backend import Backend

from bot.handlers import start_command, help_message
from bot.handlers.weather import start, end, action, time


def include_routers(dp: Dispatcher):
    dp.include_routers(start_command.router)
    dp.include_routers(help_message.router)

    dp.include_routers(
        start.router,
        end.router,
        action.router,
        time.router,
    )


async def run():
    conf: Config = load_config()
    bot = Bot(token=conf.bot_token)
    storage = MemoryStorage()
    backend = Backend(address=conf.api_url, api_key=conf.api_key)

    dp = Dispatcher(storage=storage, bot=bot, backend=backend)

    dp.message.middleware(ThrottlingMiddleware(0.5))

    include_routers(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(run())
