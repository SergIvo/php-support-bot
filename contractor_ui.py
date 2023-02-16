import logging

from environs import Env
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.callback_data import CallbackData


NEW_ORDERS = [
    {'id': 1, 'text': 'Починить админку'},
    {'id': 2, 'text': 'Мигрировать базу'},
    {'id': 3, 'text': 'Добавить форму'},
    {'id': 4, 'text': 'Доработать форму'},
    {'id': 5, 'text': 'Доработать админку'},
    {'id': 6, 'text': 'Добавить админку'},
    {'id': 7, 'text': 'Починить формы'},
    {'id': 8, 'text': 'Добавить интерфейс'},
    {'id': 9, 'text': 'Изменить базу данных'},
    {'id': 10, 'text': 'Починить ввод'},
    {'id': 11, 'text': 'Доработать авторизацию'},
    {'id': 12, 'text': 'Доработать базу данных'},
    {'id': 13, 'text': 'Поменять доступ к админке'},
    {'id': 14, 'text': 'Встроить сервис'},
    {'id': 15, 'text': 'Доработать интерфейс'},
    {'id': 16, 'text': 'Починить авторизацию'},
    {'id': 17, 'text': 'Доработать базу данных'},
    {'id': 18, 'text': 'Починить формы ввода'}
]

ORDERS_HISTORY = [
    {'id': 1, 'text': 'Встроить сервис'},
    {'id': 2, 'text': 'Доработать интерфейс'},
    {'id': 3, 'text': 'Починить авторизацию'},
    {'id': 4, 'text': 'Доработать базу данных'},
    {'id': 5, 'text': 'Починить формы ввода'}
]


class ContractorUI(StatesGroup):
    main_menu = State()
    orders_list = State()
    order = State()


inlines_cb_data = CallbackData('list_type', 'object', 'id')


async def send_main_menu(message: types.Message, state: FSMContext):
    print(type(message))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    find_orders_button = types.KeyboardButton('Найти заказ')
    my_orders_button = types.KeyboardButton('Мои заказы',)
    markup.add(find_orders_button, my_orders_button)

    await state.set_state(ContractorUI.orders_list)
    if isinstance(message, types.callback_query.CallbackQuery):
        print('Query detected ', type(message))
        await message.message.reply('Выберите действие', reply_markup=markup)
    else:
        print('Query not detected ', type(message))
        await message.reply('Выберите действие', reply_markup=markup)


async def find_order(message: types.Message):
    orders = ['Order 1', 'Order 2', 'Order 3', 'Order 4', 'Order 5']
    markup = types.InlineKeyboardMarkup(row_width=4, resize_keyboard=True)
    for i, order in enumerate(orders):
        order_button = types.InlineKeyboardButton(text=order, callback_data=f'{i}')
        markup.add(order_button)
    
    navigation_buttons = [
        types.InlineKeyboardButton(text='Назад', callback_data='menu'),
        types.InlineKeyboardButton(text='>', callback_data='forward'),
    ]
    markup.row()
    for button in navigation_buttons:
        markup.insert(button)

    await message.answer('Доступные заказы', reply_markup=markup)


async def show_order_history(message: types.Message, state: FSMContext):
    orders = NEW_ORDERS
    if isinstance(message, types.callback_query.CallbackQuery):
        orders = NEW_ORDERS
        print(dir(message))
    else:
        print(message.text)
        if 'Мои заказы' in message.text:
            orders = ORDERS_HISTORY[:5]
            reply_text = 'История заказов'
        elif 'Найти заказ' in message.text:
            orders = NEW_ORDERS[:5]
            reply_text = 'Доступные заказы'
    markup = types.InlineKeyboardMarkup(row_width=4, resize_keyboard=True)
    for order in orders:
        order_button = types.InlineKeyboardButton(order['text'], callback_data=str(order['id']))
        markup.add(order_button)
    
    navigation_buttons = [
        types.InlineKeyboardButton(text='Назад', callback_data='menu'),
        types.InlineKeyboardButton(text='>', callback_data='forward'),
    ]
    markup.row()
    for button in navigation_buttons:
        markup.insert(button)

    state = await state.get_state()
    print(state)
    if isinstance(message, types.callback_query.CallbackQuery):
        pass
    else:
        await message.answer('История заказов', reply_markup=markup)


async def some_inline_handler(callback: types.CallbackQuery):
    print(callback.message)


if __name__ == '__main__':
    env = Env()
    env.read_env()
    TG_BOT_TOKEN = env('TG_BOT_TOKEN')

    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=TG_BOT_TOKEN)
    storage = MemoryStorage()
    dispatcher = Dispatcher(bot, storage=storage)
    
    dispatcher.register_message_handler(send_main_menu, commands=['menu'], state='*')
    dispatcher.register_callback_query_handler(send_main_menu, text='menu', state='*')
    dispatcher.register_callback_query_handler(show_order_history, text=['back', 'forward'], state=ContractorUI.orders_list)
    dispatcher.register_message_handler(show_order_history, state=ContractorUI.orders_list)
    dispatcher.register_callback_query_handler(some_inline_handler, text=['1', '2', '3', '4', '5'])

    executor.start_polling(dispatcher, skip_updates=True)
