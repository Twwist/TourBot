from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.types import Message
from handlers.menu.menu import menu
from handlers.registrations.signup_user import user_password_waiting
from handlers.registrations.check import is_user_registered


start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = is_user_registered(message)
    if user:
        first_name = user.username
        await menu(message,f"👋Здравствуйте, {first_name}\nЧто Вас интересует?")
    else:
        await message.answer("👋Здравствуйте\n\n"
                             "❌<b>Вы ещё не зарегистрированы.</b>\n"
                             "Для продолжения работы пройдите регистрацию")
        await user_password_waiting(message, state)
