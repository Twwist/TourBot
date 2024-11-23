from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

# Определение базового класса для моделей
Base = declarative_base()


class Bus(Base):
    __tablename__ = 'buses'

    bus_id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String(20), nullable=False)
    brand = Column(String(50), nullable=False)
    driver_name = Column(String(50), nullable=False)
    seat_count = Column(Integer, nullable=False)
    comfort_level = Column(String(20), nullable=False)
    has_air_conditioning = Column(Boolean, nullable=False)

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
    comfort_level = Column(String(20), nullable=False)
    requires_air_conditioning = Column(Boolean, nullable=False)

    responses = relationship("Response", back_populates="request")
    user = relationship("User", back_populates="requests")


class Response(Base):
    __tablename__ = 'responses'

    response_id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey('requests.request_id'), nullable=False)
    price = Column(Float, nullable=False)

    request = relationship("Request", back_populates="responses")


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(Integer)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    requests = relationship("Request", back_populates="user")
