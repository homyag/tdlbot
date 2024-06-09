from aiogram import Router, F
from aiogram.filters import Command

from .managers import get_my_tasks


router: Router = Router(name=__name__)
router.message.filter(F.chat.type == "private")
router.message.register(get_my_tasks, Command(commands='tasks'))