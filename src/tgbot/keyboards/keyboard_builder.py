from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class CallbackCallsFactory(CallbackData, prefix="call_"):
    task_id: int

class CallbackManagersFactory(CallbackData, prefix="manager_"):
    manager_id: int

class CallbackChangeManagersFactory(CallbackData, prefix="change_manager_"):
    task_id: int
    manager_id: int

class CallbackResultsFactory(CallbackData, prefix="result_"):
    task_id: int
    result_id: int


def my_tasks_keyboard(calls):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for call in calls:
        button_text = (f"ID: {call['id']} | "
                       # f"Phone: {call['phone']} | "
                       f"Имя: {call['name']}")
        callback_data = CallbackCallsFactory(task_id=call['id']).pack()
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=button_text,
                                                              callback_data=callback_data)])
    return keyboard


def managers_keyboard(managers):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for manager in managers:
        button_text = (f"ID: {manager['id']} | "
                       f"{manager['name']}")
        callback_data = CallbackManagersFactory(manager_id=manager['id']).pack()
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=button_text,
                                                              callback_data=callback_data)])
    return keyboard

def results_keyboard(results, task_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for result in results:
        button_text = (
            f"ID: {result['id']} | "
            f"{result['name']}"
        )
        callback_data = CallbackResultsFactory(task_id=task_id, result_id=result['id']).pack()
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=button_text,
                                                              callback_data=callback_data)])
    return keyboard

def change_manager_keyboard(managers, task_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for manager in managers:
        button_text = (
            f"ID: {manager['id']} | "
            f"{manager['name']}"
        )
        callback_data = CallbackChangeManagersFactory(task_id=task_id,
                                                manager_id=manager['id']).pack()
        keyboard.inline_keyboard.append([InlineKeyboardButton(
                                                                text=button_text,
                                                                callback_data=callback_data)])
    return keyboard

def action_choice_keyboard(task_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Добавить комментарий",
                callback_data=f"edit_comment:{task_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Изменить статус",
                callback_data=f"edit_status:{task_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Передать другому менеджеру",
                callback_data=f"edit_manager:{task_id}"
            )
        ],
    ])
    return keyboard
