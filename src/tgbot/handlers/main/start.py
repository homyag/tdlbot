import logging

from aiogram.types import Message


logger = logging.getLogger(__name__)


async def command_start(message: Message) -> None:
    await message.answer(
        text="Вас приветствует бот ТДЛ-Учёт",
        reply_markup=None,
    )