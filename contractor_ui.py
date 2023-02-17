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
    {'id': 5, 'text': 'Починить формы ввода'},
    {'id': 6, 'text': 'Починить формы ввода'},
    {'id': 7, 'text': 'Починить формы ввода'},
    {'id': 8, 'text': 'Починить формы ввода'}
]


def get_orders_history(role):
    return ORDERS_HISTORY


def get_new_orders(role):
    return NEW_ORDERS


class ContractorUI(StatesGroup):
    main_menu = State()
    orders_list = State()
    order = State()


inlines_cb = CallbackData('#', 'action', 'subject')
print(inlines_cb._part_names)


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


async def show_order_history(message: types.Message, state: FSMContext):
    entries_limit = 5

    if isinstance(message, types.callback_query.CallbackQuery):
        callback_data = inlines_cb.parse(message.data)
        current_page = int(callback_data['subject'])
        print(current_page)

        if 'История заказов' in message.message.text:
            all_orders = get_orders_history('contractor')
            reply_text = 'История заказов'
        elif 'Доступные заказы' in message.message.text:
            all_orders = get_new_orders('contractor')
            reply_text = 'Доступные заказы'
        orders = all_orders[entries_limit * (current_page - 1):entries_limit * current_page]
    else:
        current_page = 1
        if 'Мои заказы' in message.text:
            all_orders = get_orders_history('contractor')
            reply_text = 'История заказов'
        elif 'Найти заказ' in message.text:
            all_orders = get_new_orders('contractor')
            reply_text = 'Доступные заказы'
        orders = all_orders[:entries_limit]

    markup = types.InlineKeyboardMarkup(row_width=4, resize_keyboard=True)
    for order in orders:
        order_cb_data = inlines_cb.new(action='view_order', subject=str(order['id']))
        order_button = types.InlineKeyboardButton(order['text'], callback_data=order_cb_data)
        markup.add(order_button)

    forward_cb_data = inlines_cb.new(action='browse_list', subject=f'{current_page + 1}')
    markup.row()
    if current_page > 1:
        back_cb_data = inlines_cb.new(action='browse_list', subject=f'{current_page - 1}')
        markup.insert(
            types.InlineKeyboardButton(text='<', callback_data=back_cb_data)
        )
    markup.insert(
        types.InlineKeyboardButton(text='Назад', callback_data='menu')
    )
    if current_page * entries_limit < len(all_orders):
        forward_cb_data = inlines_cb.new(action='browse_list', subject=f'{current_page + 1}')
        markup.insert(
            types.InlineKeyboardButton(text='>', callback_data=forward_cb_data)
        )
    markup.row()

    state = await state.get_state()
    if isinstance(message, types.callback_query.CallbackQuery):
        await message.message.edit_reply_markup(reply_markup=markup)
    else:
        await message.answer(reply_text, reply_markup=markup)


async def show_order_details(callback: types.CallbackQuery):
    callback_data = inlines_cb.parse(callback.data)
    print(callback_data)
    reply_text = 'Пока пусто'
    markup = types.InlineKeyboardMarkup(row_width=4, resize_keyboard=True)
    markup.add(
        types.InlineKeyboardButton(text='В главное меню', callback_data='menu')
    )
    await callback.message.answer(reply_text, reply_markup=markup)


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
    dispatcher.register_callback_query_handler(show_order_history, inlines_cb.filter(action='browse_list'), state=ContractorUI.orders_list)
    dispatcher.register_message_handler(show_order_history, state=ContractorUI.orders_list)
    dispatcher.register_callback_query_handler(show_order_details, inlines_cb.filter(action='view_order'), state='*')

    executor.start_polling(dispatcher, skip_updates=True)
