import logging

import requests
from aiogram.enums import ParseMode

from aiogram.types import Message

from src.tgbot.keyboards.keyboard_builder import managers_keybord

logger = logging.getLogger(__name__)

async def get_my_tasks(message: Message) -> None:
    tg_id = message.from_user.id

    start_date = '2024-04-01'
    end_date = '2024-04-30'

    API_URL = "http://127.0.0.1:8000/api/v1/calllist/filter/"

    url = f"{API_URL}?manager_tg_id={tg_id}&start_date={start_date}&end_date={end_date}"

    response = requests.get(url)

    if response.status_code == 200:
        calls = response.json()
        if calls:
            reply = (f"Список Ваших задач с {start_date} по {end_date}:\n\n "
                     f"Для добавления комментария нажмите на кнопку, "
                     f"соответствующую задаче.\n\n")
            keyboard = managers_keybord(calls)
            for call in calls:
                reply += (
                    f"ID: {call['id']}\n"
                    f"Дата звонка: {call['created']}\n"
                    # f"Источник: {call['resource']}\n"
                    f"Номер телефона: {call['phone']}\n"
                    f"Электронная почта: {call['mail']}\n"
                    f"Организация/ЧЛ: {call['name']}\n"
                    f"Комментарии: {call['comment']}\n"
                    # f"Последнее обновление: {call['updated']}\n"
                    # f"Результат: {call['result']}\n"
                    # f"Менеджер: {call['manager']}\n"
                    "\n"
                )
        else:
            reply = "Звонков не найдено в указанном диапазоне дат."
            keyboard = None
    else:
        reply = "Произошла ошибка при запросе данных."
        keyboard = None

    if keyboard:
        await message.answer(reply, reply_markup=keyboard)
    else:
        await message.answer(reply)

    # await message.answer(reply, parse_mode=ParseMode.MARKDOWN)