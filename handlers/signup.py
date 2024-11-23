from aiogram import Bot, Dispatcher, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from decouple import config
from create_bot import dp
from handlers.menu import menu

# Читаем корректный пароль из настроек
correct_password = config('REGISTRATE_PASSWORD')
signup_router = Router()


# Определение состояний FSM
class SignUp(StatesGroup):
    password = State()
    name = State()


# Ожидание пароля
async def user_password_waiting(message: types.Message, state: FSMContext):
    await message.answer(
        "🔐<b>Подтвердите, что вы являетесь водителем 'Урал батыр'.</b>\n\n"
        "Введите пароль:"
    )
    await state.set_state(SignUp.password)


# Проверка пароля
@signup_router.message(SignUp.password)
async def handle_user_password(message: types.Message, state: FSMContext):
    if message.text == correct_password:
        await message.answer("✅ <b>Пароль верный!</b>\nВведите ваше имя (например, Иван Иванов):")
        await state.set_state(SignUp.name)
    else:
        await message.answer("❌ <b>Неправильный пароль.</b> Попробуйте ещё раз.")


# Обработка имени
@signup_router.message(SignUp.name)
async def users_su(message: types.Message, state: FSMContext):
    if len(message.text.split()) != 2:
        await message.answer(
            '❌<b>Фамилия или имя введены неверно.</b> Пример корректных данных: <b>Иван Иванов</b>'
        )
        return

    # Разбиваем имя и фамилию
    first_name, last_name = message.text.split()

    # Пример сохранения данных в базу (закомментирован)
    # new_user = User(user_id=message.chat.id, first_name=first_name, last_name=last_name, post="Водитель")
    # session.add(new_user)
    # session.commit()

    # Приветствие пользователя
    await menu(
        message,
        f'👋<b>Здравствуйте, {first_name} {last_name}!</b>\n'
        f'Вы успешно зарегистрировались как <b>водитель</b>.',
    )
    await state.clear()  # Сброс состояния
