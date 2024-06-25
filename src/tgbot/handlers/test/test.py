import logging
import configparser
import os

import requests

from aiogram.types import Message

from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.environ.get('API_TOKEN')

logger = logging.getLogger(__name__)


async def command_help(message: Message) -> None:
    await message.answer(
        text='Ну вроде работает.',
        reply_markup=None,
    )

async def get_chat_id(message: Message) -> None:
    await message.answer(
        text=f'Ваш ID: {message.chat.id}',
        reply_markup=None,
    )


# async def get_data_from_api(message: Message) -> None:
#
#     tg_id = '59726568'
#     API_URL = "http://127.0.0.1:8000/api/v1/callslist/filter/"
#
#     start_date = '2024-06-23'
#     end_date = '2024-06-25'
#
#     url = f"{API_URL}?manager_tg_id={tg_id}&start_date={start_date}&end_date={end_date}"
#
#     headers = {'Authorization': f'{API_TOKEN}'}
#
#     response = requests.get(url, headers=headers)
#
#     if response.status_code == 200:
#         calls = response.json()
#         print(calls)
#         if calls:
#             reply = (f"Список Ваших задач с {start_date} по {end_date}:\n\n "
#                      f"Для добавления комментария нажмите на кнопку, "
#                      f"соответствующую задаче.\n\n")
#             for call in calls:
#                 reply += (
#                     f"<b>ID:</b> {call['id']}\n"
#                     f"<b>Дата звонка:</b> {call['created']}\n"
#                     f"<b>Номер телефона:</b> {call['phone']}\n"
#                     f"<b>Электронная почта:</b> {call['mail']}\n"
#                     f"<b>Организация/ЧЛ:</b> {call['name']}\n"
#                     f"<b>Комментарии:</b> {call['comment']}\n"
#                     # f"Результат: {call['result']}\n"
#                     "\n"
#                 )
#         else:
#             reply = "Задач в указанном диапазоне дат не найдено."
#     else:
#         reply = "Что-то пошло не так. Произошла ошибка при запросе данных."
#
#     if reply:
#         await message.answer(reply, reply_markup=None)
#     else:
#         await message.answer(reply, parse_mode=None)
