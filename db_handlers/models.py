from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey, ARRAY
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Base class for models (не нужно дважды определять Base)
Base = declarative_base()

# Table "Users"
# Table "Users"

ase = declarative_base()


class Bus(Base):
    __tablename__ = 'buses'

    tg_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    bus_id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String(20), nullable=False)
    brand = Column(String(50), nullable=False)
    driver_name = Column(String(50), nullable=False)

    type_bus = Column(String, nullable=False)

    condition = Column(Boolean, nullable=False)
    microphone_for_guide = Column(Boolean, nullable=False)
    monitor = Column(Boolean, nullable=False)
    arm_chairs = Column(Boolean, nullable=False)

    responses = relationship("Response", back_populates="bus")

    schedules = relationship("Schedule", back_populates="bus")


class Schedule(Base):
    __tablename__ = 'schedules'

    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    bus_id = Column(Integer, ForeignKey('buses.bus_id'), nullable=False)
    date_range = Column(String(100), nullable=False)

    bus = relationship("Bus", back_populates="schedules")


class Request(Base):
    __tablename__ = 'requests'

    request_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    route = Column(String(255), nullable=False)
    date_range = Column(String(100), nullable=False)

    minivan = Column(Boolean, nullable=False)
    microbus = Column(Boolean, nullable=False)
    small_bus = Column(Boolean, nullable=False)
    medium_bus = Column(Boolean, nullable=False)
    big_bus = Column(Boolean, nullable=False)
    large_bus = Column(Boolean, nullable=False)

    condition = Column(Boolean, nullable=False)
    microphone_for_guide = Column(Boolean, nullable=False)
    monitor = Column(Boolean, nullable=False)
    arm_chairs = Column(Boolean, nullable=False)

    status = Column(String(255), nullable=False)
    send_or_no = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="requests")

    responses = relationship("Response", back_populates="request")


class Response(Base):
    __tablename__ = 'responses'

    response_id = Column(Integer, primary_key=True, autoincrement=True)  # Идентификатор отклика
    user_id = Column(Integer, ForeignKey('users.user_id'),
                     nullable=False)  # Идентификатор пользователя, который оставил отклик
    bus_id = Column(Integer, ForeignKey('buses.bus_id'),
                    nullable=False)  # Идентификатор пользователя, который оставил отклик
    request_id = Column(Integer, ForeignKey('requests.request_id'),
                        nullable=False)  # Идентификатор заказа, на который сделан отклик
    price = Column(Float, nullable=False)  # Цена, за которую пользователь готов выполнить заказ

    # Определяем связь с таблицей Request (для получения связанных данных о заказе)
    request = relationship("Request", back_populates="responses")

    # Определяем связь с таблицей User (для получения связанных данных о пользователе)
    user = relationship("User", back_populates="responses")

    bus = relationship("Bus", back_populates="responses")


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer)
    phone_number = Column(String(20), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    requests = relationship("Request", back_populates="user")

    responses = relationship("Response", back_populates="user")

    @property
    def is_active(self):
        return True

    def get_id(self):
        return str(self.user_id)
