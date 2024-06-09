from aiogram import Router, F
from aiogram.filters import Command

from .test import command_help, get_chat_id

router: Router = Router(name=__name__)
router.message.filter(F.chat.type == "private")
router.message.register(command_help, Command(commands='help'))
router.message.register(get_chat_id, Command(commands='get_id'))