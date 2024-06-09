from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def managers_keybord(calls):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[], row_width=7)
    for call in calls:
        button_text = (f"ID: {call['id']} | "
                       # f"Phone: {call['phone']} | "
                       f"Имя: {call['name']}")
        callback_data = f"call_{call['id']}"
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=button_text,
                                                              callback_data=callback_data)])
    return keyboard