import logging

import asyncio
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog.setup import DialogRegistry

from src.tgbot.handlers.managers_handlers import managers_new_task, managers_tasks

from src.tgbot.config.config import Config, load_config
from src.tgbot.database.connect import create_async_engine_db, \
    async_connection_db
from src.tgbot.middlewares import (
    SessionMiddleware,
    RegisteredMiddleware,
    AuthorizationMiddleware,
)
from src.tgbot.handlers import (
    main, test, managers_handlers,
)
from src.tgbot.middlewares.api_mdlw import ApiTokenMiddleware

from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.environ.get('API_TOKEN')

logger = logging.getLogger(__name__)


async def start_app(configfile):
    # -> Logging
    logging.basicConfig(
        format="[%(asctime)s] [%(name)s] [%(levelname)s] > %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )
    logger.debug("-> Bot online")

    # -> Config
    config: Config = load_config(configfile)

    # -> Storage
    storage = MemoryStorage()

    # -> SQLAlchemy
    db_session = await async_connection_db(
        engine=await create_async_engine_db(
            config=config.db,
            echo=config.settings.sqlalchemy_echo,
        ),
        expire_on_commit=config.settings.sqlalchemy_expire_on_commit,
    )

    # -> BOT
    bot: Bot = Bot(
        token=config.tg_bot.token,
        parse_mode=config.settings.default_parse_mode,
    )
    dp: Dispatcher = Dispatcher(storage=storage)

    # -> Middlewares
    dp.update.middleware(AuthorizationMiddleware(bot))
    dp.update.middleware(ApiTokenMiddleware(API_TOKEN))
    dp.update.middleware(SessionMiddleware(sessionmaker=db_session))
    dp.update.middleware(RegisteredMiddleware())

    # -> Registerer Routers
    dp.include_router(main.router)
    dp.include_router(test.router)
    # dp.include_router(managers_handlers.router)
    dp.include_router(managers_new_task.router)
    dp.include_router(managers_tasks.router)

    # -> Start
    await bot.delete_webhook(drop_pending_updates=True)
    # -> delete menu button
    #await bot.delete_my_commands()
    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
    )
