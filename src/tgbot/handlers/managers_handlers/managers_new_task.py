import logging
import requests
import os

from datetime import datetime

from dotenv import load_dotenv

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State, default_state

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.utils.formatting import Text

from src.tgbot.keyboards.keyboard_builder import my_tasks_keyboard, \
    CallbackCallsFactory, managers_keyboard, CallbackManagersFactory
from src.tgbot.services.apps import get_managers

load_dotenv()

API_TOKEN = os.environ.get('API_TOKEN')

logger = logging.getLogger(__name__)

router = Router()



class FSMNewTask(StatesGroup):
    customer_name = State()
    customer_phone = State()
    customer_mail = State()
    resource = State()
    comment_for_manager = State()
    choose_manager = State()
    result = State()

@router.message(Command(commands='newtask'), StateFilter(default_state))
async def process_new_task(message: Message, state: FSMContext):
    await message.answer(text="Введите имя клиента или компании:")
    await state.set_state(FSMNewTask.customer_name)

@router.message(StateFilter(FSMNewTask.customer_name))
async def process_customer_name(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(customer_name=message.text)
        await message.answer(text="Пожалуйста, введите телефон клиента:")
        await state.set_state(FSMNewTask.customer_phone)
    else:
        await message.answer(text="Что то пошло не так. Повторите попытку "
                                  "введя команду.")
        await state.clear()

@router.message(StateFilter(FSMNewTask.customer_phone))
async def process_customer_phone(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(customer_phone=message.text)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="email_yes")],
            [InlineKeyboardButton(text="Нет", callback_data="email_no")]
            ]
        )
        await message.answer(text="Известна ли почта клиента?",
                             reply_markup=keyboard)
        await state.set_state(FSMNewTask.customer_mail)
    else:
        await message.answer(text="Что то пошло не так. Повторите попытку "
                                  "введя команду.")
        await state.clear()

@router.callback_query(StateFilter(FSMNewTask.customer_mail))
async def process_customer_mail_callback(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "email_yes":
        await callback_query.message.answer("Пожалуйста, введите электронную почту клиента:")
    elif callback_query.data == "email_no":
        await state.update_data(customer_mail="")
        await callback_query.message.answer(text="Пожалуйста, укажите источник лида:")
        await state.set_state(FSMNewTask.resource)

@router.message(StateFilter(FSMNewTask.customer_mail))
async def process_customer_mail(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(customer_mail=message.text)
        await message.answer(text="Пожалуйста, укажите источник лида:")
        await state.set_state(FSMNewTask.resource)

    else:
        await message.answer(text="Что то пошло не так. Повторите попытку "
                                  "введя команду.")
        await state.clear()

@router.message(StateFilter(FSMNewTask.resource))
async def process_resource(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(resource=message.text)
        await message.answer(text="Пожалуйста, введите комментарий для "
                                  "менеджера:")
        await state.set_state(FSMNewTask.comment_for_manager)
    else:
        await message.answer(text="Что то пошло не так. Повторите попытку "
                                  "введя команду.")
        await state.clear()

@router.message(StateFilter(FSMNewTask.comment_for_manager))
async def process_comment_for_manager(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(comment_for_manager=message.text)

        managers = get_managers()

        if managers:
            keyboard = managers_keyboard(managers)
            await message.answer(text="Пожалуйста, выберите ответственного "
                                  "менеджера:", reply_markup=keyboard)
            await state.set_state(FSMNewTask.choose_manager)
        else:
            await message.answer(
                text="Что-то пошло не так. Повторите попытку, введя команду.")
            await state.clear()

@router.callback_query(CallbackManagersFactory.filter(), StateFilter(FSMNewTask.choose_manager))
async def process_choose_manager(callback_query: CallbackQuery,
                               callback_data: CallbackCallsFactory,
                               state: FSMContext):
    manager_id = callback_data.manager_id
    await state.update_data(choose_manager=manager_id)
    data = await state.get_data()

    payload = {
        'name': data['customer_name'],
        'phone': data['customer_phone'],
        'resource': data['resource'],
        'mail': data['customer_mail'],
        'comment': data['comment_for_manager'],
        'manager': manager_id,
        'result': "6"
    }

    # API_URL_NEW_TASK = 'http://127.0.0.1:8000/api/v1/callslist/'
    API_URL_NEW_TASK = 'https://tdleningrad.ru/api/v1/callslist/'
    headers = {'Authorization': f'{API_TOKEN}'}

    response = requests.post(API_URL_NEW_TASK, json=payload, headers=headers)

    if response.status_code == 201:
        await callback_query.message.answer("Задача успешно создана.")
        await state.clear()
    else:
        await callback_query.message.answer(
            "Произошла ошибка при создании задачи.")
        await state.clear()