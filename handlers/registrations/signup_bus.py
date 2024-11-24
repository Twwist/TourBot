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
    has_air_conditioning = State()
    mic_for_guide = State()
    tv_monitor = State()
    reclining_seats = State()
    category = State()
    confirmation = State()


# Роутер для регистрации автобуса
bus_router = Router()


# Старт регистрации автобуса
async def bus_registration(message: types.Message, state: FSMContext):
    await message.answer(
        "🚌 <b>Нужно зарегистрировать автобус</b>\n\n"
        "Введите номер автобуса:"
    )
    await state.set_state(SignUpBus.number)


# Ввод номера автобуса
@bus_router.message(SignUpBus.number)
async def handle_bus_number(message: types.Message, state: FSMContext):
    number = message.text
    await state.update_data(number=number)
    await message.answer("🚍 Введите марку автобуса:")
    await state.set_state(SignUpBus.brand)


# Ввод марки автобуса
@bus_router.message(SignUpBus.brand)
async def handle_bus_brand(message: types.Message, state: FSMContext):
    brand = message.text
    await state.update_data(brand=brand)
    air_conditioner_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Да✅"), KeyboardButton(text="Нет❌")]],
        resize_keyboard=True
    )
    await message.answer("❄️ Есть ли кондиционер в автобусе?", reply_markup=air_conditioner_keyboard)
    await state.set_state(SignUpBus.has_air_conditioning)


# Ввод информации о кондиционере
@bus_router.message(SignUpBus.has_air_conditioning)
async def handle_air_conditioner(message: types.Message, state: FSMContext):
    has_air_conditioning = message.text.lower()
    if has_air_conditioning not in ["да✅", "нет❌"]:
        await message.answer("❌ Выберите 'Да✅' или 'Нет❌' с помощью кнопок.")
        return
    await state.update_data(has_air_conditioning=(has_air_conditioning == "да✅"))

    mic_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Да✅"), KeyboardButton(text="Нет❌")]],
        resize_keyboard=True
    )
    await message.answer("🎤 Есть ли микрофон для гида?", reply_markup=mic_keyboard)
    await state.set_state(SignUpBus.mic_for_guide)


# Ввод информации о микрофоне
@bus_router.message(SignUpBus.mic_for_guide)
async def handle_mic_for_guide(message: types.Message, state: FSMContext):
    mic_for_guide = message.text.lower()
    if mic_for_guide not in ["да✅", "нет❌"]:
        await message.answer("❌ Выберите 'Да✅' или 'Нет❌' с помощью кнопок.")
        return
    await state.update_data(mic_for_guide=(mic_for_guide == "да✅"))

    tv_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Да✅"), KeyboardButton(text="Нет❌")]],
        resize_keyboard=True
    )
    await message.answer("📺 Есть ли монитор/ТВ?", reply_markup=tv_keyboard)
    await state.set_state(SignUpBus.tv_monitor)


# Ввод информации о мониторе/ТВ
@bus_router.message(SignUpBus.tv_monitor)
async def handle_tv_monitor(message: types.Message, state: FSMContext):
    tv_monitor = message.text.lower()
    if tv_monitor not in ["да✅", "нет❌"]:
        await message.answer("❌ Выберите 'Да✅' или 'Нет❌' с помощью кнопок.")
        return
    await state.update_data(tv_monitor=(tv_monitor == "да✅"))

    recline_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Да✅"), KeyboardButton(text="Нет❌")]],
        resize_keyboard=True
    )
    await message.answer("🛋️ Есть ли откидные кресла?", reply_markup=recline_keyboard)
    await state.set_state(SignUpBus.reclining_seats)


# Ввод информации об откидных креслах
@bus_router.message(SignUpBus.reclining_seats)
async def handle_reclining_seats(message: types.Message, state: FSMContext):
    reclining_seats = message.text.lower()
    if reclining_seats not in ["да✅", "нет❌"]:
        await message.answer("❌ Выберите 'Да✅' или 'Нет❌' с помощью кнопок.")
        return
    await state.update_data(reclining_seats=(reclining_seats == "да✅"))

    category_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Минивены (5-9 мест)")],
            [KeyboardButton(text="Микроавтобусы (10-20 мест)")],
            [KeyboardButton(text="Малые автобусы (21-30 мест)")],
            [KeyboardButton(text="Средние автобусы (31-45 мест)")],
            [KeyboardButton(text="Большие автобусы (46-60 мест)")],
            [KeyboardButton(text="Особо большие автобусы (61-90 мест)")]
        ],
        resize_keyboard=True
    )
    await message.answer("🚐 Выберите категорию транспорта:", reply_markup=category_keyboard)
    await state.set_state(SignUpBus.category)


# Ввод категории транспорта
@bus_router.message(SignUpBus.category)
async def handle_category(message: types.Message, state: FSMContext):
    type_bus = message.text
    valid_categories = [
        "Минивены (5-9 мест)", "Микроавтобусы (10-20 мест)", "Малые автобусы (21-30 мест)",
        "Средние автобусы (31-45 мест)", "Большие автобусы (46-60 мест)", "Особо большие автобусы (61-90 мест)"
    ]
    if type_bus not in valid_categories:
        await message.answer("❌ Выберите категорию из предложенных.")
        return
    await state.update_data(type_bus=type_bus)

    # Вывод итоговых данных
    data = await state.get_data()
    await message.answer(
        f"✅ <b>Данные автобуса:</b>\n\n"
        f"🔷 Номер: {data['number']}\n"
        f"🔷 Марка: {data['brand']}\n"
        f"🔷 Кондиционер: {'Да✅' if data['has_air_conditioning'] else 'Нет❌'}\n"
        f"🔷 Микрофон для гида: {'Да✅' if data['mic_for_guide'] else 'Нет❌'}\n"
        f"🔷 Монитор/ТВ: {'Да✅' if data['tv_monitor'] else 'Нет❌'}\n"
        f"🔷 Откидные кресла: {'Да✅' if data['reclining_seats'] else 'Нет❌'}\n"
        f"🔷 Категория: {data['type_bus']}"
    )

    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Всё верно", callback_data="confirm_data")],
            [InlineKeyboardButton(text="❌ Не верно", callback_data="cancel_data")]
        ]
    )
    await message.answer("🔄 Всё верно? Отправляем данные?", reply_markup=confirm_keyboard)
    await state.set_state(SignUpBus.confirmation)


# Обработка инлайн-кнопок
@bus_router.callback_query(SignUpBus.confirmation)
async def handle_confirmation(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "confirm_data":
        # Получаем данные из состояния
        data = await state.get_data()
        tg_id = callback.from_user.id
        number = data["number"]
        brand = data["brand"]

        # Получаем имя водителя из базы данных
        user = session.query(User).filter(User.tg_id == tg_id).first()
        driver_name = user.username if user else "Неизвестно"
        user_id = user.user_id

        # Извлекаем остальные данные
        type_bus = data["type_bus"]  # Категория автобуса (например, тип)
        condition = data["has_air_conditioning"]  # Кондиционер
        microphone_for_guide = data["mic_for_guide"]  # Микрофон для гида
        monitor = data["tv_monitor"]  # Монитор/ТВ
        arm_chairs = data["reclining_seats"]  # Откидные кресла

        # Создаем новый экземпляр автобуса
        new_bus = Bus(
            tg_id=tg_id,
            user_id=user_id,
            number=number,
            brand=brand,
            driver_name=driver_name,
            type_bus=type_bus,
            condition=condition,
            microphone_for_guide=microphone_for_guide,
            monitor=monitor,
            arm_chairs=arm_chairs
        )

        # Сохраняем автобус в базе данных
        session.add(new_bus)
        session.commit()

        # Уведомляем пользователя об успешном сохранении
        await menu(callback, "🚀 Данные успешно сохранены! Спасибо!")
        await state.clear()
    elif callback.data == "cancel_data":
        # Если данные неверны, перезапускаем процесс регистрации
        await callback.message.answer("❌ Регистрация отменена. Начнём заново.")
        await state.clear()
        await bus_registration(callback.message, state)
