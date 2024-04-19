from aiogram import Router, F
from aiogram.filters import Command

from .test import command_help

router: Router = Router(name=__name__)
router.message.filter(F.chat.type == "private")
router.message.register(command_help, Command(commands='test'))