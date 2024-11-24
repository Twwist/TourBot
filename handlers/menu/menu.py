from aiogram import types
from aiogram.types import ReplyKeyboardMarkup

from create_bot import bot


async def menu(message, message_text: str):
    """
    Отправляет главное меню
    :param message: сообщение от пользователя
    :param message_text: текст сообщения
    """

    buttons_type = ['🚌Мой автобус', '📋Предложения', '🗓Расписание']

    buttons = [types.KeyboardButton(text=text) for text in buttons_type]
    return_menu = ReplyKeyboardMarkup(
        keyboard=[
            [buttons[1]],  # "📋Предложения" на первом ряду
            [buttons[0], buttons[2]]  # "🚌Мой автобус" и "🗓Расписание" на втором ряду
        ],
        resize_keyboard=True
    )

    await bot.send_message(message.from_user.id, message_text, reply_markup=return_menu)

