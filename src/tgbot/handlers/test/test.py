import logging

from aiogram.types import Message

logger = logging.getLogger(__name__)


async def command_help(message: Message) -> None:
    await message.answer(
        text='Ну вроде получилось',
        reply_markup=None,
    )
