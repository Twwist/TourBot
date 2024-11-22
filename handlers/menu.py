from aiogram import types
from create_bot import bot


async def menu(message, message_text: str, menu_type: str):
    """
    Отправляет главное меню
    :param message: сообщение от пользователя
    :param message_text: текст сообщения
    :param menu_type: тип меню:
            'choice' - Меню для выбора типа пользователя
            'operator' - Меню тур-оператора
            'driver' - Меню водителя
    """

    if menu_type not in ('choice', 'operator', 'driver'):
        raise ValueError('Недопустимое значение menu_type')

    buttons_type = {'choice': ['Тур-оператор', 'Водитель'],
                    'operator': ['Найти автобус', 'Избранное', 'Текущий сеанс'],
                    'driver': ['Добавить автобус', 'Мои автобусы', 'Предложения', 'Текущий сеанс']}

    buttons = [types.KeyboardButton(text=text) for text in buttons_type[menu_type]]
    return_menu = types.ReplyKeyboardMarkup(
        keyboard=[
            buttons
        ],
        resize_keyboard=True,
        row_width=2)

    await bot.send_message(message.from_user.id, message_text, reply_markup=return_menu)

