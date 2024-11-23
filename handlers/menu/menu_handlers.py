from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import and_

from db_handlers.create_db import session
from db_handlers.models import Request, Response, Bus, User, Schedule
from handlers.registrations.check import is_bus_registered, is_user_registered
from handlers.registrations.signup_bus import bus_registration
from handlers.registrations.signup_user import user_password_waiting
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

menu_router = Router()


class ResponseAnswer(StatesGroup):
    waiting_for_price = State()


@menu_router.message(lambda message: message.text == "🚌Мой автобус")
async def my_buses(message: types.Message, state: FSMContext):
    if is_user_registered(message):
        # Проверяем, есть ли зарегистрированные автобусы
        bus = is_bus_registered(message)
        if bus:
            # Отображаем информацию о зарегистрированном автобусе
            await message.answer("<b>Ваш автобус:</b>\n"
                                 f"<b>Номер</b>: {bus.number}\n"
                                 f"<b>Марка</b>: {bus.brand}\n"
                                 f"<b>Кондиционер</b>: {'Есть' if bus.condition else 'Нет'}\n"
                                 f"<b>Микрофон для гида</b>: {'Есть' if bus.microphone_for_guide else 'Нет'}\n"
                                 f"<b>Монитор/ТВ</b>: {'Есть' if bus.monitor else 'Нет'}\n"
                                 f"<b>Откидные кресла</b>: {'Есть' if bus.arm_chairs else 'Нет'}\n"
                                 f"<b>Тип</b>: {bus.type_bus}")
        else:
            await message.answer("❌У вас нет зарегистрированных автобусов.")
            await bus_registration(message, state)
    else:
        await message.answer("❌Вы не зарегистрированы.")
        await user_password_waiting(message, state)


@menu_router.message(lambda message: message.text == "📋Предложения")
async def offers(message: types.Message, state: FSMContext):
    if is_user_registered(message):
        bus = is_bus_registered(message)  # Проверяем, есть ли зарегистрированные автобусы
        if bus:
            # Ищем подходящие заказы
            matching_requests = session.query(Request).filter(
                and_(
                    # Фильтрация по типу автобуса с учетом точного совпадения строки
                    (Request.minivan == (bus.type_bus == "Минивены (5-9 мест)")) |
                    (Request.microbus == (bus.type_bus == "Микроавтобусы (10-20 мест)")) |
                    (Request.small_bus == (bus.type_bus == "Малые автобусы (21-30 мест)")) |
                    (Request.medium_bus == (bus.type_bus == "Средние автобусы (31-45 мест)")) |
                    (Request.big_bus == (bus.type_bus == "Большие автобусы (46-60 мест)")) |
                    (Request.large_bus == (bus.type_bus == "Особо большие автобусы (61-90 мест)")),

                    # Проверка, что маршруты не совпадают с уже зарегистрированными
                    ~Request.date_range.in_([schedule.date_range for schedule in bus.schedules]),

                    # Фильтрация по наличию удобств
                    bus.condition or Request.condition == bus.condition,
                    bus.microphone_for_guide or Request.microphone_for_guide == bus.microphone_for_guide,
                    bus.monitor or Request.monitor == bus.monitor,
                    bus.arm_chairs or Request.arm_chairs == bus.arm_chairs
                )
            ).all()

            # Формируем ответ
            if matching_requests:
                response_text = "Доступные вам заказы:\n\n"
                keyboard = InlineKeyboardMarkup(inline_keyboard=[], row_width=1)

                for idx, request in enumerate(matching_requests, start=1):
                    # Формируем текст заказа
                    response_text += (
                        f"<b>Маршрут</b>: {request.route}\n"
                        f"<b>Даты</b>: {request.date_range}\n"
                        f"<b>Уровень комфорта</b>: {'Высокий' if request.condition else 'Низкий'}\n"
                        f"<b>Кондиционер</b>: {'Есть' if request.condition else 'Нет'}\n"
                        f"<b>Микрофон для гида</b>: {'Есть' if request.microphone_for_guide else 'Нет'}\n"
                        f"<b>Монитор / ТВ</b>: {'Есть' if request.monitor else 'Нет'}\n"
                        f"<b>Откидные кресла</b>: {'Есть' if request.arm_chairs else 'Нет'}\n\n"
                    )

                    # Создаем кнопку для отклика на заказ
                    button = InlineKeyboardButton(
                        text=f"☑️Откликнуться на {idx} заказ",
                        callback_data=f"apply_for_request_{idx}_{request.request_id}"
                    )
                    keyboard.inline_keyboard.append([button])

                await message.answer(response_text, reply_markup=keyboard)
            else:
                await message.answer("🤷‍♂️Нет подходящих заказов для вашего автобуса.")
        else:
            await message.answer("❌У вас нет зарегистрированных автобусов.")
            await bus_registration(message, state)
    else:
        await message.answer("❌Вы не зарегистрированы.")
        await user_password_waiting(message, state)


# Обработка отклика на заказ
@menu_router.callback_query(lambda callback_query: callback_query.data.startswith('apply_for_request_'))
async def apply_for_request(callback: types.CallbackQuery, state: FSMContext):
    # Извлекаем индекс и ID заказа из callback_data
    data = callback.data.split("_")
    request_idx = int(data[3])  # Индекс заказа (например, 1, 2, 3)
    request_id = int(data[4])  # ID самого заказа

    # Запрашиваем цену отклика
    await callback.message.answer(f"💰Вы хотите откликнуться на заказ №{request_idx}. Сколько вы готовы запросить за выполнение этого заказа?")
    await state.update_data(request_id=request_id)  # Сохраняем ID запроса в состоянии
    await state.set_state(ResponseAnswer.waiting_for_price)


# Обработка введенной цены
@menu_router.message(ResponseAnswer.waiting_for_price)
async def handle_price(message: types.Message, state: FSMContext):
    # Получаем введенную цену
    price = message.text

    # Проверка на корректность введенной цены (например, это должно быть число)
    if not price.isdigit():
        await message.answer("Пожалуйста, введите правильную цену (число).")
        return

    price = int(price)  # Преобразуем введенную цену в число

    # Получаем ID заказа из состояния
    data = await state.get_data()
    request_id = data.get("request_id")
    user = session.query(User).filter(User.tg_id == message.from_user.id).first()
    bus = session.query(Bus).filter(Bus.user_id == user.user_id).first()

    # Находим заказ в базе данных
    request = session.query(Request).filter(Request.request_id == request_id).first()

    if request:
        # Создаем отклик на заказ
        response = Response(
            user_id=user.user_id,
            bus_id=bus.bus_id,
            request_id=request_id,
            price=price
        )

        # Добавляем отклик в базу данных
        session.add(response)
        session.commit()

        await message.answer(f"Вы откликнулись на заказ №{request_id} с ценой {price} руб. Ваш отклик был успешно сохранен!")
        await state.clear()  # Очищаем состояние
    else:
        await message.answer("Ошибка! Не удалось найти этот заказ.")
        await state.clear()  # Очищаем состояние


@menu_router.message(lambda message: message.text == "🗓Расписание")
async def current_session(message: Message, state: FSMContext):
    # Проверяем, зарегистрирован ли пользователь
    user = session.query(User).filter(User.tg_id == message.from_user.id).first()
    if user:
        # Проверяем, есть ли у пользователя зарегистрированные автобусы
        buses = session.query(Bus).filter(Bus.tg_id == user.tg_id).all()
        if buses:
            response = "Ваше расписание:\n\n"
            for bus in buses:
                schedules = session.query(Schedule).filter(Schedule.bus_id == bus.bus_id).all()
                if schedules:
                    response += f"🚍 Автобус {bus.number} ({bus.brand})\n"
                    for schedule in schedules:
                        response += f"📅 Даты: {schedule.date_range}\n"
                    response += "\n"
                else:
                    response += f"🚍 Автобус {bus.number} ({bus.brand}) пока не имеет расписания.\n\n"
            await message.answer(response)
        else:
            await message.answer("У вас нет зарегистрированных автобусов.")
            await bus_registration(message, state)
    else:
        await message.answer("Вы не зарегистрированы.")
        await user_password_waiting(message, state)
