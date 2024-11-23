from aiogram import types
from create_bot import bot


async def menu(message, message_text: str):
    """
    Отправляет главное меню
    :param message: сообщение от пользователя
    :param message_text: текст сообщения
    """

    buttons_type = ['Мой автобусы', 'Предложения', 'Расписание']

    buttons = [types.KeyboardButton(text=text) for text in buttons_type]
    return_menu = types.ReplyKeyboardMarkup(
        keyboard=[
            buttons
        ],
        resize_keyboard=True,
        row_width=2)

    await bot.send_message(message.from_user.id, message_text, reply_markup=return_menu)

