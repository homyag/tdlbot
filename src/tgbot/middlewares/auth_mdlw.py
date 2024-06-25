import logging
import configparser

from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.handlers import message
from aiogram.types import Message, CallbackQuery, TelegramObject, user, User

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('bot.ini')

AUTHORIZED_USERS = config.get('AUTHORIZED_USERS', 'ids').split(',')

def is_user_authorized(user_id: int) -> bool:
    logger.debug(f"Checking authorization for user_id: {user_id}")
    authorized = str(user_id) in AUTHORIZED_USERS
    logger.debug(f"Authorization result for user_id {user_id}: {authorized}")
    return authorized

class AuthorizationMiddleware(BaseMiddleware):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    async def __call__(
            self,
            handler: Callable[
                [TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user: User = data.get("event_from_user")
        if user is not None:
            if not is_user_authorized(user.id):
                logger.warning(f"User {user.id} {user.full_name} is not authorized")
                await self.bot.send_message(user.id, "Вам отказано в "
                                                     "доступе. Обратитесь к "
                                                     "администратору")
                return
            return await handler(event, data)