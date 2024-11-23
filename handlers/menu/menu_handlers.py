from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy import and_

from db_handlers.create_db import session
from db_handlers.models import Request
from handlers.registrations.check import is_bus_registered, is_user_registered
from handlers.registrations.signup_bus import bus_registration
from handlers.registrations.signup_user import user_password_waiting

menu_router = Router()


@menu_router.message(lambda message: message.text == "Мой автобусы")
async def my_buse(message: types.Message, state: FSMContext):
    if is_user_registered(message):
        bus = is_bus_registered(message)
        if bus:
            await message.answer("<b>Ваш автобус:</b>\n"
                                 f"🔹 Номер: {bus.number}\n"
                                 f"🔹 Марка: {bus.brand}\n"
                                 f"🔹 Мест: {bus.seat_count}\n"
                                 f"🔹 Комфорт: {bus.comfort_level}\n"
                                 f"🔹 Кондиционер: {'Есть' if bus.has_air_conditioning else 'Нет'}")
        else:
            await message.answer("У вас нет зарегистрированных автобусов.")
            await bus_registration(message, state)
    else:
        await message.answer("Вы не зарегистрированы.")
        await user_password_waiting(message, state)


@menu_router.message(lambda message: message.text == "Предложения")
async def offers(message: types.Message, state: FSMContext):
    if is_user_registered(message):
        bus = is_bus_registered(message)  # Проверяем, есть ли зарегистрированные автобусы
        if bus:
            # Ищем подходящие заказы
            matching_requests = session.query(Request).filter(
                and_(
                    Request.seat_count == bus.seat_count,
                    Request.comfort_level == bus.comfort_level,
                    Request.requires_air_conditioning == bus.has_air_conditioning,
                    ~Request.date_range.in_([schedule.date_range for schedule in bus.schedules])
                )
            ).all()
            print(matching_requests)
            # print(Request.date_range)

            # Формируем ответ
            if matching_requests:
                response_text = "Доступные вам заказы:\n\n"
                for request in matching_requests:
                    response_text += (
                        f"🛣️ Маршрут: {request.route}\n"
                        f"📅 Даты: {request.date_range}\n"
                        f"💺 Уровень комфорта: {request.comfort_level}\n"
                        f"❄️ Кондиционер: {'Да' if request.requires_air_conditioning else 'Нет'}\n\n"
                    )
                await message.answer(response_text)
            else:
                await message.answer("Нет подходящих заказов для вашего автобуса.")
        else:
            await message.answer("У вас нет зарегистрированных автобусов.")
            await bus_registration(message, state)
    else:
        await message.answer("Вы не зарегистрированы.")
        await user_password_waiting(message, state)


@menu_router.message(lambda message: message.text == "Расписание")
async def current_session(message: types.Message, state: FSMContext):
    if is_user_registered(message):
        if is_bus_registered(message):
            await message.answer("Ваше расписание:")
        else:
            await message.answer("У вас нет зарегистрированных автобусов.")
            await bus_registration(message, state)
    else:
        await message.answer("Вы не зарегистрированы.")
        await user_password_waiting(message, state)

