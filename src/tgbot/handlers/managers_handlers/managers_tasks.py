import configparser
import logging
import os
import requests

from datetime import datetime
from dotenv import load_dotenv

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.types import Message, CallbackQuery

from src.tgbot.keyboards.keyboard_builder import my_tasks_keyboard, \
    CallbackCallsFactory, CallbackResultsFactory, results_keyboard, \
    action_choice_keyboard, managers_keyboard, change_manager_keyboard, \
    CallbackChangeManagersFactory
from src.tgbot.services.apps import is_valid_date, get_managers
from src.tgbot.services.apps import get_results

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('bot.ini')
OPERATOR_IDS = config.get('operator_ids', 'ids').split(',')

load_dotenv()

API_TOKEN = os.environ.get('API_TOKEN')

router = Router()

class FSMGetTasksForm(StatesGroup):
    start_date = State()
    end_date = State()

class FSMPostComment(StatesGroup):
    waiting_for_comment = State()

@router.message(Command(commands='mytasks'), StateFilter(default_state))
async def process_start_date(message: Message, state: FSMContext):
    await message.answer(text="Пожалуйста введите дату начала в формате YYYY-MM-DD")
    await state.set_state(FSMGetTasksForm.start_date)

@router.message(StateFilter(FSMGetTasksForm.start_date))
async def process_end_date(message: Message, state: FSMContext):
    if is_valid_date(message.text):
        await state.update_data(start_date=message.text)
        await message.answer(text="Пожалуйста введите дату окончания в формате YYYY-MM-DD")
        await state.set_state(FSMGetTasksForm.end_date)
    else:
        await message.answer(text="Неверный формат даты. Пожалуйста введите "
                                  "дату начала в "
                                  "формате YYYY-MM-DD")

@router.message(StateFilter(FSMGetTasksForm.end_date))
async def warning_end_date(message: Message, state: FSMContext):
    if is_valid_date(message.text):
        await state.update_data(end_date=message.text)
        data = await state.get_data()

        start_date = data.get('start_date')
        end_date = data.get('end_date')

        await message.answer(text=f"Вы выбрали даты: {start_date} - {end_date}")
        await get_my_tasks(message, start_date, end_date)

        await state.clear()

    else:
        await message.answer(text="Неверный формат даты. Пожалуйста введите "
                                  "дату окончания в формате YYYY-MM-DD")
async def get_my_tasks(message: Message, start_date: str, end_date: str) -> None:
    tg_id = message.from_user.id

    # API_URL = "http://127.0.0.1:8000/api/v1/callslist/filter/"
    API_URL = "https://tdleningrad.ru/api/v1/callslist/filter/"

    url = f"{API_URL}?manager_tg_id={tg_id}&start_date={start_date}&end_date={end_date}"

    headers = {'Authorization': f'{API_TOKEN}'}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        calls = response.json()
        if calls:
            reply = (f"Список Ваших задач с {start_date} по {end_date}:\n\n "
                     f"Для добавления комментария нажмите на кнопку, "
                     f"соответствующую задаче.\n\n")
            keyboard = my_tasks_keyboard(calls)
            for call in calls:
                reply += (
                    f"<b>ID:</b> {call['id']}\n"
                    f"<b>Дата звонка:</b> {call['created']}\n"
                    f"<b>Номер телефона:</b> {call['phone']}\n"
                    f"<b>Электронная почта:</b> {call['mail']}\n"
                    f"<b>Организация/ЧЛ:</b> {call['name']}\n"
                    f"<b>Комментарии:</b> {call['comment']}\n"
                    # f"Результат: {call['result']}\n"
                    "\n"
                )
        else:
            reply = "Задач в указанном диапазоне дат не найдено."
            keyboard = None
    else:
        reply = "Что-то пошло не так. Произошла ошибка при запросе данных."
        keyboard = None

    if keyboard:
        await message.answer(reply, reply_markup=keyboard)
    else:
        await message.answer(reply, parse_mode=ParseMode.MARKDOWN)


@router.callback_query(CallbackCallsFactory.filter())
async def process_task_action(callback_query: CallbackQuery,
                              callback_data: CallbackCallsFactory,
                              state: FSMContext):
    task_id = callback_data.task_id
    await state.update_data(task_id=task_id)
    keyboard = action_choice_keyboard(task_id)
    await callback_query.message.answer(text="Выберите действие:",
                                        reply_markup=keyboard)

@router.callback_query(lambda c: c.data and c.data.startswith('edit_comment'))
async def process_edit_comment_choice(callback_query: CallbackQuery, state: FSMContext):
    task_id = callback_query.data.split(':')[1]
    await state.update_data(task_id=task_id)
    await callback_query.message.answer(text="Пожалуйста, введите комментарий")
    await state.set_state(FSMPostComment.waiting_for_comment)

@router.callback_query(lambda c: c.data and c.data.startswith('edit_status'))
async def process_edit_status_choice(callback_query: CallbackQuery,
                                     state: FSMContext):
    task_id = callback_query.data.split(':')[1]
    await state.update_data(task_id=task_id)
    results = get_results()

    if results:
        keyboard = results_keyboard(results, task_id)
        await callback_query.message.answer(text="Выберите новый статус "
                                                 "заявки:",
                                            reply_markup=keyboard)

@router.callback_query(lambda c: c.data and c.data.startswith(
'edit_manager'))
async def process_edit_manager_choice(callback_query: CallbackQuery,
                                      state: FSMContext):
    task_id = callback_query.data.split(':')[1]
    await state.update_data(task_id=task_id)
    managers = get_managers()
    if managers:
        keyboard = change_manager_keyboard(managers, task_id)
        await callback_query.message.answer(text="Назначить нового "
                                                 "менеджера:",
                                            reply_markup=keyboard)

@router.callback_query(CallbackChangeManagersFactory.filter())
async def process_edit_manager(callback_query: CallbackQuery,
                               callback_data: CallbackChangeManagersFactory,
                               state: FSMContext):
    task_id = callback_data.task_id
    manager_id = callback_data.manager_id
    await state.update_data(task_id=task_id)

    # Вызов API для получения информации о менеджере
    # API_GET_MANAGER_URL = f'http://127.0.0.1:8000/api/v1/managers/'
    API_GET_MANAGER_URL = f'https://tdleningrad.ru/api/v1/managers/'

    headers = {'Authorization': f'{API_TOKEN}'}

    response = requests.get(API_GET_MANAGER_URL, headers=headers)

    if response.status_code == 200:
        managers = response.json()
        # Поиск имени менеджера по ID
        manager_name = next((manager['name'] for manager in managers if
                             manager['id'] == manager_id),
                            'Неизвестный менеджер')
        manager_tg_id = next((manager['tg_id'] for manager in managers if
                             manager['id'] == manager_id),
                            'Менеджер не оставил TG ID')
    else:
        manager_name = 'Неизвестный менеджер'

    # API_PATCH_URL = f'http://127.0.0.1:8000/api/v1/callslist/manager_update/{task_id}/'
    API_PATCH_URL = f'https://tdleningrad.ru/api/v1/callslist/manager_update/{task_id}/'
    headers = {'Authorization': f'{API_TOKEN}'}
    payload = {'manager': manager_id}
    response = requests.patch(API_PATCH_URL, json=payload, headers=headers)

    if response.status_code == 200:
        await callback_query.message.answer("Статус успешно обновлен.")
        await callback_query.message.bot.send_message(
            chat_id=manager_tg_id,
            text=f"<i>Пользователь {callback_query.from_user.full_name} "
                 f"передал Вам задачу № "
                 f" <b>{task_id}</b></i>"

        )
        for operator_id in OPERATOR_IDS:
            await callback_query.message.bot.send_message(
                chat_id=operator_id,
                text=f"\n\nПользователь"
                     f" <b>{callback_query.from_user.full_name}</b> "
                     f"изменил менеджера в заявке"
                     f" <b>{task_id}</b>. "
                     f"Новый менеджер: <b>{manager_name}</b>.")
    else:
        await callback_query.message.answer(
            "Произошла ошибка при обновлении статуса.")

        await state.clear()

@router.callback_query(CallbackResultsFactory.filter())
async def process_edit_result(callback_query: CallbackQuery,
                              callback_data: CallbackResultsFactory,
                              state: FSMContext):
    task_id = callback_data.task_id
    result_id = callback_data.result_id
    await state.update_data(task_id=task_id)

    # API_PATCH_URL = f'http://127.0.0.1:8000/api/v1/callslist/result_update/{task_id}/'
    API_PATCH_URL = f'https://tdleningrad.ru/api/v1/callslist/result_update/{task_id}/'

    payload = {'result': result_id}
    headers = {'Authorization': f'{API_TOKEN}'}

    response = requests.patch(API_PATCH_URL, json=payload, headers=headers)

    if response.status_code == 200:
        await callback_query.message.answer("Статус успешно обновлен.")
        for operator_id in OPERATOR_IDS:
            await callback_query.message.bot.send_message(
                chat_id=operator_id,
                text=f"\n\n<b>Пользователь"
                     f" {callback_query.from_user.full_name} "
                     f"изменил статус заявки"
                     f" {task_id}.</b>")
    else:
        await callback_query.message.answer(
            "Произошла ошибка при обновлении статуса.")

    await state.clear()

@router.callback_query(CallbackCallsFactory.filter())
async def process_edit_comment(callback_query: CallbackQuery,
                               callback_data: CallbackCallsFactory,
                               state: FSMContext):
    task_id = callback_data.task_id
    await state.update_data(task_id=task_id)
    await callback_query.message.answer(text="Пожалуйста, введите комментарий")
    await state.set_state(FSMPostComment.waiting_for_comment)

@router.message(StateFilter(FSMPostComment.waiting_for_comment))
async def process_comment(message: Message, state: FSMContext):
    user_data = await state.get_data()
    task_id = user_data['task_id']
    comment = message.text
    # API_GET_URL = f'http://127.0.0.1:8000/api/v1/callslist/call/{task_id}/'
    API_GET_URL = f'https://tdleningrad.ru/api/v1/callslist/call/{task_id}/'
    # API_PATCH_URL = f"http://127.0.0.1:8000/api/v1/callslist/comment_update/{task_id}/"
    API_PATCH_URL = f"https://tdleningrad.ru/api/v1/callslist/comment_update/{task_id}/"
    # получаем текущий комментарий
    headers = {'Authorization': f'{API_TOKEN}'}
    response = requests.get(API_GET_URL, headers=headers)
    if response.status_code == 200:
        current_comment = response.json().get('comment', '')
        current_date = datetime.now().strftime('[%d.%m.%Y]')
        new_comment = f"{current_date} {message.from_user.full_name} {comment}"

        if current_comment:
            new_comment = f"{current_comment}\n{new_comment}"

        payload = {'comment': new_comment}

        response = requests.patch(API_PATCH_URL, json=payload, headers=headers)

        if response.status_code == 200:
            await message.answer("Комментарий успешно обновлен.\n Новый "
                                 "комментарий:\n" + new_comment)
            # отправка сообщения оператору
            for operator_id in OPERATOR_IDS:
                await message.bot.send_message(
                    chat_id=operator_id,
                    text=f"В задаче {task_id} добавлен новый комментарий:\n"
                         f" {new_comment}")
        else:
            await message.answer("Произошла ошибка при обновлении комментария.")
    else:
        await message.answer("Не удалось получить комментарий")

    await state.clear()