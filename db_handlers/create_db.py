from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_handlers.models import Base  # Импортируем Base из models.py

from decouple import config

DATABASE = {
    'user': 'myuser',
    'password': 'mypassword',
    'host': '45.90.216.229',  # Или IP-адрес сервера
    'port': '5432',       # Стандартный порт PostgreSQL
    'database': 'my_database_name'
}
db_url = f"postgresql+psycopg2://{DATABASE['user']}:{DATABASE['password']}@{DATABASE['host']}:{DATABASE['port']}/{DATABASE['database']}"
engine = create_engine(db_url)
# Создание всех таблиц в базе данных
Base.metadata.create_all(engine)

# Сессия для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()

print("Database and tables have been created!")
