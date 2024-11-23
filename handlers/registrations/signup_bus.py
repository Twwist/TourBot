from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from db_handlers.create_db import session
from db_handlers.models import User, Bus
from handlers.menu.menu import menu


# FSM для регистрации автобуса
class SignUpBus(StatesGroup):
    number = State()
    brand = State()
    seat_count = State()
    comfort_level = State()
    has_air_conditioning = State()
    confirmation = State()


# Роутер для регистрации автобуса
bus_router = Router()


# Старт регистрации автобуса
async def bus_registration(message: types.Message, state: FSMContext):
    await message.answer(
        "🚌 <b>Теперь нужно зарегистрировать автобус</b>\n\n"
        "Введите номер автобуса:"
    )
    await state.set_state(SignUpBus.number)


# Ввод номера автобуса
@bus_router.message(SignUpBus.number)
async def handle_bus_number(message: types.Message, state: FSMContext):
    number = message.text
    await state.update_data(number=number)
    await message.answer("Введите марку автобуса:")
    await state.set_state(SignUpBus.brand)


# Ввод марки автобуса
@bus_router.message(SignUpBus.brand)
async def handle_bus_brand(message: types.Message, state: FSMContext):
    brand = message.text
    await state.update_data(brand=brand)
    await message.answer("Введите количество мест в автобусе:")
    await state.set_state(SignUpBus.seat_count)


# Ввод количества мест
@bus_router.message(SignUpBus.seat_count)
async def handle_seats_count(message: types.Message, state: FSMContext):
    seat_count = message.text
    if not seat_count.isdigit():
        await message.answer("Количество мест должно быть числом. Попробуйте ещё раз.")
        return
    await state.update_data(seat_count=int(seat_count))
    await message.answer(
        "Укажите уровень комфорта автобуса по шкале от 1 до 5:\n"
        "1 - отвратительно, 2 - плохо, 3 - нормально, 4 - хорошо, 5 - очень комфортно."
    )
    await state.set_state(SignUpBus.comfort_level)


# Ввод уровня комфорта
@bus_router.message(SignUpBus.comfort_level)
async def handle_comfort_level(message: types.Message, state: FSMContext):
    comfort_level = message.text
    if not comfort_level.isdigit() or not (1 <= int(comfort_level) <= 5):
        await message.answer("Введите число от 1 до 5.")
        return
    await state.update_data(comfort_level=int(comfort_level))

    # Кнопки для выбора наличия кондиционера
    air_conditioner_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
        ],
        resize_keyboard=True
    )
    await message.answer("Есть ли кондиционер в автобусе?", reply_markup=air_conditioner_keyboard)
    await state.set_state(SignUpBus.has_air_conditioning)


# Ввод информации о кондиционере
@bus_router.message(SignUpBus.has_air_conditioning)
async def handle_air_conditioner(message: types.Message, state: FSMContext):
    has_air_conditioning = message.text.lower()
    if has_air_conditioning not in ["да", "нет"]:
        await message.answer("Выберите 'Да' или 'Нет' с помощью кнопок.")
        return
    await state.update_data(has_air_conditioning=(has_air_conditioning == "да"))

    # Показываем итоговые данные
    data = await state.get_data()

    await message.answer(
        f"✅ <b>Данные автобуса:</b>\n\n"
        f"🔹 Номер: {data['number']}\n"
        f"🔹 Марка: {data['brand']}\n"
        f"🔹 Мест: {data['seat_count']}\n"
        f"🔹 Комфорт: {data['comfort_level']}\n"
        f"🔹 Кондиционер: {'Да' if data['has_air_conditioning'] else 'Нет'}"
    )

    # Инлайн-кнопки для подтверждения
    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Всё верно", callback_data="confirm_data")],
            [InlineKeyboardButton(text="❌ Не верно", callback_data="cancel_data")]
        ]
    )
    await message.answer("Всё верно? Отправляем данные?", reply_markup=confirm_keyboard)
    await state.set_state(SignUpBus.confirmation)


# Обработка инлайн-кнопок
@bus_router.callback_query(SignUpBus.confirmation)
async def handle_confirmation(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "confirm_data":
        data = await state.get_data()
        tg_id = callback.from_user.id
        number = data["number"]
        brand = data['brand']

        user = session.query(User).filter(
            User.tg_id == tg_id).first()
        driver_name = user.username

        seat_count = data['seat_count']
        comfort_level = data['comfort_level']
        has_air_conditioning = data['has_air_conditioning']

        new_bus = Bus(
            number=number,
            brand=brand,
            driver_name=driver_name,
            seat_count=seat_count,
            comfort_level=comfort_level,
            has_air_conditioning=has_air_conditioning
        )

        # Добавляем автобус в сессию и сохраняем в базе данных
        session.add(new_bus)
        session.commit()
        await menu(callback, "🚀 Данные успешно сохранены! Спасибо!")
        await state.clear()
    elif callback.data == "cancel_data":
        await callback.message.answer("❌ Регистрация отменена. Начнём заново.")
        await state.clear()
        await bus_registration(callback.message, state)
