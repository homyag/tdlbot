import logging

from aiogram.types import Message


logger = logging.getLogger(__name__)


async def command_start(message: Message) -> None:
    await message.answer(
        text="Вас приветствует бот ТДЛ-Учёт!\nЧтобы получить список своих "
             "задач введите команду /mytasks\nЧтобы добавить новую задачу "
             "введите команду /newtask",
        reply_markup=None,
    )