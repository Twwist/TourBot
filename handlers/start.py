from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from handlers.menu import menu
from handlers.signup import user_password_waiting


def is_registered(message):
    user_id = message.from_user.id
    user = False  # {'first_name': message.from_user.first_name}
    # user = session.query(User).filter(User.user_id == user_id).first()

    if user:
        return user
    else:
        return False


start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = is_registered(message)
    if user:
        first_name = user['first_name']
        await menu(message,f"👋Здравствуйте, {first_name}\nЧто Вас интересует?")
    else:
        await message.answer("👋Здравствуйте\n\n"
                             "❌<b>Вы ещё не зарегистрированы.</b>\n"
                             "Для продолжения работы пройдите регистрацию")
        await user_password_waiting(message, state)
