from aiogram import Router, types

menu_router = Router()


@menu_router.message(lambda message: message.text == "Добавить автобус")
async def add_bus(message: types.Message):
    await message.answer("Введите информацию о новом автобусе.")


@menu_router.message(lambda message: message.text == "Мои автобусы")
async def my_buses(message: types.Message):
    await message.answer("Вот список ваших автобусов.")


@menu_router.message(lambda message: message.text == "Предложения")
async def offers(message: types.Message):
    await message.answer("Здесь вы видите доступные предложения.")


@menu_router.message(lambda message: message.text == "Текущий сеанс")
async def current_session(message: types.Message):
    await message.answer("Вы сейчас находитесь в текущем сеансе.")
