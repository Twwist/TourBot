from aiogram import Bot, Dispatcher, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from decouple import config
from create_bot import dp
from handlers.menu import menu

# Читаем корректный пароль из настроек
correct_password = config('REGISTRATE_PASSWORD')
router = Router()


# Определение состояний FSM
class SignUp(StatesGroup):
    password = State()
    name = State()
    post = State()


# Ожидание пароля
async def user_password_waiting(message: types.Message, state: FSMContext):
    await message.answer(
        "🔐<b>Подтвердите, что вы сотрудник 'Урал батыр' или являетесь водителем.</b>\n\n"
        "Введите пароль:",
        parse_mode="HTML"
    )
    await state.set_state(SignUp.password)


# Проверка пароля
@router.message(SignUp.password)
async def handle_user_password(message: types.Message, state: FSMContext):
    if message.text == correct_password:
        await menu(message, "✅ <b>Пароль верный!</b>\nКакая у вас должность?", 'choice')
        await state.set_state(SignUp.post)
    else:
        await message.answer("❌ <b>Неправильный пароль.</b> Попробуйте ещё раз.", parse_mode="HTML")


# Получение должности через кнопки
@router.message(SignUp.post)
async def handle_user_post(message: types.Message, state: FSMContext):
    post = message.text
    # Проверка, что должность выбрана из кнопок
    if post not in ['Тур-оператор', 'Водитель']:
        await message.answer("❌ <b>Неверный выбор должности.</b> Пожалуйста, выберите одну из предложенных кнопок.",
                             parse_mode="HTML")
        return

    # Сохраняем должность в данных FSM
    await state.update_data(post=post)
    # Убираем клавиатуру после выбора должности
    await message.answer("✅ <b>Должность сохранена!</b>\nВведите ваше имя (например, Иван Иванов):", parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(SignUp.name)


# Обработка имени
@router.message(SignUp.name)
async def users_su(message: types.Message, state: FSMContext):
    if len(message.text.split()) != 2:
        await message.answer(
            '❌<b>Фамилия или имя введены неверно.</b> Пример корректных данных: <b>Иван Иванов</b>',
            parse_mode="HTML"
        )
        return

    # Разбиваем имя и фамилию
    first_name, last_name = message.text.split()
    # Сохраняем данные в FSM
    data = await state.get_data()
    post = data.get("post")

    # Пример сохранения в базу данных (код закомментирован)
    # new_user = User(user_id=message.chat.id, first_name=first_name, last_name=last_name, post=post)
    # session.add(new_user)
    # session.commit()

    # Приветствие пользователя
    await menu(
        message,
        f'👋<b>Здравствуйте, {first_name} {last_name}!</b>\n'
        f'Вы успешно зарегистрировались как <b>{post}</b>.',
        'operator' if post == 'Тур-оператор' else 'driver'
    )
    await state.clear()  # Сброс состояния-но


# Регистрация маршрутов
dp.include_router(router)
