import logging
from typing import Union

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


def get_order(orders_list, order_id):
    return {'id': order_id, 'list': orders_list, 'text': 'Текст заказа'}


class ContractorUI(StatesGroup):
    orders_list = State()
    order = State()


navigation_cb = CallbackData('#', 'order_list','page')
order_cb = CallbackData('#', 'order_list', 'list_page', 'order_id', 'status')



async def send_main_menu(event: Union[types.Message, types.callback_query.CallbackQuery], state: FSMContext):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    find_orders_button = types.KeyboardButton('Найти заказ')
    my_orders_button = types.KeyboardButton('Мои заказы',)
    markup.add(find_orders_button, my_orders_button)

    await state.set_state(ContractorUI.orders_list)
    if isinstance(event, types.callback_query.CallbackQuery):
        await event.message.reply('Выберите действие', reply_markup=markup)
    else:
        await event.reply('Выберите действие', reply_markup=markup)


async def show_order_history(event: Union[types.Message, types.callback_query.CallbackQuery], state: FSMContext):
    entries_limit = 5

    if isinstance(event, types.callback_query.CallbackQuery):
        callback_data = navigation_cb.parse(event.data)
        current_page = int(callback_data['page'])

        if callback_data['order_list'] == 'history':
            all_orders = get_orders_history('contractor')
            reply_text = 'История заказов'
        elif callback_data['order_list'] == 'new':
            all_orders = get_new_orders('contractor')
            reply_text = 'Доступные заказы'
        orders = all_orders[entries_limit * (current_page - 1):entries_limit * current_page]
        order_list_type = callback_data['order_list']
    else:
        current_page = 1
        if 'Мои заказы' in event.text:
            all_orders = get_orders_history('contractor')
            reply_text = 'История заказов'
            order_list_type = 'history'
        elif 'Найти заказ' in event.text:
            all_orders = get_new_orders('contractor')
            reply_text = 'Доступные заказы'
            order_list_type = 'new'
        orders = all_orders[:entries_limit]

    markup = types.InlineKeyboardMarkup(row_width=4, resize_keyboard=True)
    for order in orders:
        order_cb_data = order_cb.new(
            order_list=order_list_type,
            list_page=current_page,
            order_id=str(order['id']),
            status=''
        )
        order_button = types.InlineKeyboardButton(order['text'], callback_data=order_cb_data)
        markup.add(order_button)

    forward_cb_data = navigation_cb.new(
        order_list=order_list_type, 
        page=f'{current_page + 1}'
    )
    markup.row()
    if current_page > 1:
        back_cb_data = navigation_cb.new(
            order_list=order_list_type, 
            page=f'{current_page - 1}'
        )
        markup.insert(
            types.InlineKeyboardButton(text='<', callback_data=back_cb_data)
        )
    markup.insert(
        types.InlineKeyboardButton(text='Назад', callback_data='menu')
    )
    if current_page * entries_limit < len(all_orders):
        forward_cb_data = navigation_cb.new(
            order_list=order_list_type, 
            page=f'{current_page + 1}'
        )
        markup.insert(
            types.InlineKeyboardButton(text='>', callback_data=forward_cb_data)
        )
    markup.row()

    state = await state.get_state()
    if isinstance(event, types.callback_query.CallbackQuery):
        await event.message.edit_text(reply_text, reply_markup=markup)
    else:
        await event.answer(reply_text, reply_markup=markup)


async def show_order_details(callback: types.CallbackQuery, state: FSMContext):
    state = await state.get_state()
    callback_data = order_cb.parse(callback.data)
    order = get_order(callback_data['order_list'], callback_data['order_id'])

    reply_text = ', '.join([f'{key}: {value}' for key, value in order.items()])
    markup = types.InlineKeyboardMarkup(row_width=4, resize_keyboard=True)

    if callback_data['order_list'] == 'new':
        button_cb_data = order_cb.new(
            order_list='history',
            list_page=1,
            order_id=str(order['id']),
            status='in_progress'
        )
        markup.add(
            types.InlineKeyboardButton(text='Взять в работу', callback_data=button_cb_data)
        )
    elif callback_data['order_list'] == 'history':
        markup.add(
            types.InlineKeyboardButton(text='История переписки', callback_data='nothing')
        )
        
    back_cb_data = navigation_cb.new(
        order_list=callback_data['order_list'], 
        page=callback_data['list_page']
    )
    markup.add(
        types.InlineKeyboardButton(text='К списку заказов', callback_data=back_cb_data)
    )
    await callback.message.edit_text(reply_text, reply_markup=markup)


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
    dispatcher.register_callback_query_handler(show_order_history, navigation_cb.filter(), state=ContractorUI.orders_list)
    dispatcher.register_message_handler(show_order_history, state=ContractorUI.orders_list)
    dispatcher.register_callback_query_handler(show_order_details, order_cb.filter(), state='*')

    executor.start_polling(dispatcher, skip_updates=True)
