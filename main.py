import asyncio
from create_bot import bot, dp

from handlers.registrations.start import start_router
from handlers.registrations.signup_user import signup_router
from handlers.menu.menu_handlers import menu_router
from handlers.registrations.signup_bus import bus_router
from notificarion import on_start


# from work_time.time_func import send_time_msg

async def main():
    # scheduler.add_job(send_time_msg, 'interval', seconds=10)
    # scheduler.start()
    dp.include_router(start_router)
    dp.include_router(signup_router)
    dp.include_router(menu_router)
    dp.include_router(bus_router)

    await on_start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
