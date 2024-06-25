import logging
import configparser

from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject, user, User

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('bot.ini')

class ApiTokenMiddleware(BaseMiddleware):
    def __init__(self, api_token: str):
        self.api_token = api_token

    async def __call__(
            self,
            handler: Callable[
                [TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # передача токена в data для использования в хендлерах
        data["api_token"] = self.api_token
        return await handler(event, data)