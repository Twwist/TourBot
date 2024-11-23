from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_handlers.models import Base  # Импортируем Base из models.py

from decouple import config

# Подключение к базе данных
DATABASE_URL = config('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=True)

# Создание всех таблиц в базе данных
Base.metadata.create_all(engine)

# Сессия для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()

print("Database and tables have been created!")
