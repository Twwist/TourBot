from sqlalchemy.orm import sessionmaker
from db_handlers.models import User
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
    user_id = message.from_user.id
    user = False  # {'first_name': message.from_user.first_name}
    # user = session.query(User).filter(User.user_id == user_id).first()

    if user:
        return user
    else:
        return False
