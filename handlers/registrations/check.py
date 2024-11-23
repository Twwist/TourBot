from sqlalchemy.orm import sessionmaker
from db_handlers.models import User, Bus
from db_handlers.create_db import session


def is_user_registered(message):
    tg_id = message.from_user.id

    # Запрос к базе данных для поиска пользователя с соответствующим user_id
    user = session.query(User).filter(
        User.tg_id == tg_id).first()  # Используем tg_id, так как user_id может быть внутренним

    if user:
        return user  # Возвращаем найденного пользователя
    else:
        return False  # Если пользователь не найден, возвращаем False


def is_bus_registered(message):
    tg_id = message.from_user.id

    # Запрос к базе данных для поиска пользователя с соответствующим user_id
    bus = session.query(Bus).filter(
        Bus.tg_id == tg_id).first()  # Используем tg_id, так как user_id может быть внутренним

    if bus:
        return bus  # Возвращаем найденного пользователя
    else:
        return False  # Если пользователь не найден, возвращаем False
