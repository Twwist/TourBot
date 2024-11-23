from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from decouple import config
from handlers.menu.menu import menu
from handlers.registrations.signup_bus import bus_registration
from db_handlers.create_db import Session, session
from db_handlers.models import User

# Читаем корректный пароль из настроек
correct_password = config('REGISTRATE_PASSWORD')
signup_router = Router()


# Определение состояний FSM
class SignUpUser(StatesGroup):
    password = State()
    name = State()


# Ожидание пароля
async def user_password_waiting(message: types.Message, state: FSMContext):
    await message.answer(
        "🔐<b>Подтвердите, что вы являетесь водителем 'Урал батыр'.</b>\n\n"
        "Введите пароль:"
    )
    await state.set_state(SignUpUser.password)


# Проверка пароля
@signup_router.message(SignUpUser.password)
async def handle_user_password(message: types.Message, state: FSMContext):
    if message.text == correct_password:
        await message.answer("✅ <b>Пароль верный!</b>\nВведите ваше имя (например, Иван Иванов):")
        await state.set_state(SignUpUser.name)
    else:
        await message.answer("❌ <b>Неправильный пароль.</b> Попробуйте ещё раз.")


# Обработка имени
@signup_router.message(SignUpUser.name)
async def users_su(message: types.Message, state: FSMContext):
    if len(message.text.split()) != 2:
        await message.answer(
            '❌<b>Фамилия или имя введены неверно.</b> Пример корректных данных: <b>Иван Иванов</b>'
        )
        return

    # Разбиваем имя и фамилию
    first_name, last_name = message.text.split()
    tg_id = message.from_user.id
    password = '1234'
    role = 'driver'

    new_user = User(
        tg_id=tg_id,
        username=f"{first_name}_{last_name}",  # Можно использовать уникальное имя, если оно необходимо
        password=password,
        role=role
    )

    # Добавляем пользователя в сессию и сохраняем в базе данных
    session.add(new_user)
    session.commit()

    # Приветствие пользователя
    await message.answer(
        f'👋<b>Здравствуйте, {first_name} {last_name}!</b>\n'
        f'Вы успешно зарегистрировались как <b>водитель</b>. Ваш пароль: <b>{password}</b>'
    )

    # Переход к регистрации автобуса
    await bus_registration(message, state)

