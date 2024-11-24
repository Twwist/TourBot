import asyncio

from sqlalchemy import and_

from create_bot import bot, dp
from db_handlers.models import *
from db_handlers.create_db import *
from handlers.registrations.start import start_router
from handlers.registrations.signup_user import signup_router
from handlers.menu.menu_handlers import menu_router
from handlers.registrations.signup_bus import bus_router
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()


async def send_message():
    try:
        # Create a session inside the async function
        with Session() as session:
            unsent_requests = session.query(Request).filter(Request.send_or_no == None).all()
            for request in unsent_requests:
                # Inside the send_message function
                type_bus_filters = []
                if bool(request.minivan):
                    type_bus_filters.append('Минивены (5-9 мест)')
                if bool(request.microbus):
                    type_bus_filters.append('Микроавтобусы (10-20 мест)')
                if bool(request.small_bus):
                    type_bus_filters.append('Малые автобусы (21-30 мест)')
                if bool(request.medium_bus):
                    type_bus_filters.append('Средние автобусы (31-45 мест)')
                if bool(request.big_bus):
                    type_bus_filters.append('Большие автобусы (46-60 мест)')
                if bool(request.large_bus):
                    type_bus_filters.append('Особо большие автобусы (61-90 мест)')

                # Query with the dynamically built type_bus list
                suitable_buses = session.query(Bus).filter(
                    and_(
                        Bus.type_bus.in_(type_bus_filters) if type_bus_filters else True,
                        (Bus.microphone_for_guide == request.microphone_for_guide),
                        (Bus.monitor == request.monitor),
                        (Bus.arm_chairs == request.arm_chairs)
                    )
                ).all()

                for bus in suitable_buses:
                    await bot.send_message(chat_id=bus.tg_id,
                                           text='🛎Вам доступна новая работа.\n'
                                                ' Для подробностей, перейдите в "📋Предложения"')

            # Mark the requests as sent
            session.query(Request).update(
                {Request.send_or_no: True}, synchronize_session='fetch')
            session.commit()

    except Exception as e:
        print(f"Error while sending message: {e}")


# Function to start the scheduler
async def on_start():
    # Start sending messages every 24 hours
    scheduler.add_job(send_message, IntervalTrigger(seconds=5))  # 24 hours
    scheduler.start()
