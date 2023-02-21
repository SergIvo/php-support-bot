import logging
from typing import Union
from urllib.parse import urljoin

import requests
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

env = Env()
env.read_env()
TG_BOT_TOKEN = env('TG_BOT_TOKEN')
API_BASE_URL = env('API_BASE_URL')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TG_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


def make_api_request(endpoint, method='GET', payload=None):
    url = urljoin(API_BASE_URL, endpoint)
    if method == 'POST':
        response = requests.post(url, json=payload)
    elif method == 'PUT':
        response = requests.put(url, json=payload)
    else:
        response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_contractor(telegram_id):
    order = make_api_request(f'contractor/{telegram_id}')
    return order


def get_contractor_orders(telegram_id=None, new=False):
    if new:
        new_orders = make_api_request('order/get_new/')
        return new_orders
    orders_history = make_api_request(f'contractor/orders/{telegram_id}')
    return orders_history


def get_client_orders(telegram_id=None):
    orders_history = make_api_request(f'client/orders/{telegram_id}')
    return orders_history


def get_order(order_id):
    order = make_api_request(f'order/get_or_update/{order_id}')
    return order


def get_order_chat(order_id, requester):
    conversation_roles = {
        'CLIENT': 'Заказчик',
        'CONTRACTOR': 'Исполнитель'
    }
    chat_messages = make_api_request(f'message/get_all/{order_id}')
    history = []
    for message in chat_messages:
        if message['sender'] == requester:
            history.append('Вы:')
        else:
            history.append(f'{conversation_roles[message["sender"]]}:')
        history.append(message['text'])
    formatted_history = '\n'.join(history)
    return formatted_history


def send_chat_message(sender, order_id, text):
    payload = {
        'sender': sender,
        'order': order_id,
        'text': text
    }
    make_api_request('message/create/', method='POST', payload=payload)


def send_order_update(order_id, **updates):
    order_fields = get_order(order_id)
    for field, update in updates.items():
        print(field, update)
        if field in order_fields.keys():
            order_fields[field] = update
    print(order_fields)
    resp = make_api_request(f'order/get_or_update/{order_id}', method='PUT', payload=order_fields)
    print(resp)


class ContractorUI(StatesGroup):
    orders_list = State()
    order_editing = State()


navigation_cb = CallbackData('#', 'order_list', 'page')
order_cb = CallbackData('#', 'order_list', 'list_page', 'order_id', 'status')
order_chat_cb = CallbackData('#', 'order_id', 'action')


@dp.message_handler(commands=['menu'], state='*')
@dp.callback_query_handler(text='menu', state='*')
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


@dp.callback_query_handler(navigation_cb.filter(order_list=['new', 'history']), state=ContractorUI.orders_list)
@dp.message_handler(state=ContractorUI.orders_list)
async def show_order_history(event: Union[types.Message, types.callback_query.CallbackQuery], state: FSMContext):
    entries_limit = 5

    if isinstance(event, types.callback_query.CallbackQuery):
        callback_data = navigation_cb.parse(event.data)
        current_page = int(callback_data['page'])
        telegram_id = event.message.chat.id

        if callback_data['order_list'] == 'history':
            all_orders = get_contractor_orders(telegram_id)
            reply_text = 'История заказов'
        elif callback_data['order_list'] == 'new':
            all_orders = get_contractor_orders(telegram_id, new=True)
            reply_text = 'Доступные заказы'
        orders = all_orders[entries_limit * (current_page - 1):entries_limit * current_page]
        order_list_type = callback_data['order_list']
    else:
        telegram_id = event.chat.id
        current_page = 1
        if 'Мои заказы' in event.text:
            all_orders = get_contractor_orders(telegram_id)
            reply_text = 'История заказов'
            order_list_type = 'history'
        elif 'Найти заказ' in event.text:
            all_orders = get_contractor_orders(telegram_id, new=True)
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
        order_button = types.InlineKeyboardButton(order['title'], callback_data=order_cb_data)
        markup.add(order_button)

    markup.row()
    if current_page > 1:
        back_button_cb = navigation_cb.new(
            order_list=order_list_type,
            page=f'{current_page - 1}'
        )
        markup.insert(
            types.InlineKeyboardButton(text='<', callback_data=back_button_cb)
        )
    markup.insert(
        types.InlineKeyboardButton(text='Назад', callback_data='menu')
    )
    if current_page * entries_limit < len(all_orders):
        forward_button_cb = navigation_cb.new(
            order_list=order_list_type,
            page=f'{current_page + 1}'
        )
        markup.insert(
            types.InlineKeyboardButton(text='>', callback_data=forward_button_cb)
        )
    markup.row()

    state = await state.get_state()
    if isinstance(event, types.callback_query.CallbackQuery):
        await event.message.edit_text(reply_text, reply_markup=markup)
    else:
        await event.answer(reply_text, reply_markup=markup)


@dp.callback_query_handler(order_cb.filter(), state='*')
async def show_order_details(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(ContractorUI.orders_list)

    callback_data = order_cb.parse(callback.data)
    order = get_order(callback_data['order_id'])
    
    if callback_data['status'] and callback_data['status'] != order['status']:
        contractor = get_contractor(callback.message.chat.id)
        send_order_update(
            callback_data['order_id'], 
            status=callback_data['status'], 
            contractor=contractor['id']
        )

    reply_text = ', '.join([f'{key}: {value}' for key, value in order.items()])
    markup = types.InlineKeyboardMarkup(row_width=4, resize_keyboard=True)

    if order['status'] == 'NOT_ASSIGNED':
        assign_button_cb = order_cb.new(
            order_list='history',
            list_page=1,
            order_id=callback_data['order_id'],
            status='IN_PROGRESS'
        )
        markup.add(
            types.InlineKeyboardButton(text='Взять в работу', callback_data=assign_button_cb)
        )
    else:
        chat_button_cb = order_chat_cb.new(
            order_id=callback_data['order_id'],
            action='view'
        )
        markup.add(
            types.InlineKeyboardButton(text='Смотреть переписку', callback_data=chat_button_cb)
        )
    if order['status'] == 'IN_PROGRESS':
        finish_button_cb = order_cb.new(
            order_list='history',
            list_page=1,
            order_id=callback_data['order_id'],
            status='FINISHED'
        )
        markup.add(
            types.InlineKeyboardButton(text='Закрыть заказ', callback_data=finish_button_cb)
        )

    back_button_cb = navigation_cb.new(
        order_list=callback_data['order_list'],
        page=callback_data['list_page']
    )
    markup.add(
        types.InlineKeyboardButton(text='К списку заказов', callback_data=back_button_cb)
    )
    await callback.message.edit_text(reply_text, reply_markup=markup)


@dp.callback_query_handler(order_chat_cb.filter(action='view'), state='*')
@dp.message_handler(state=ContractorUI.order_editing)
async def show_order_chat(event: Union[types.Message, types.callback_query.CallbackQuery], state: FSMContext):
    await state.set_state(ContractorUI.order_editing)
    context_data = await state.get_data()
    
    if isinstance(event, types.callback_query.CallbackQuery):
        callback_data = order_chat_cb.parse(event.data)
        order_id = callback_data['order_id']
        reply_text = get_order_chat(order_id, "CONTRACTOR")
        if not reply_text:
            reply_text = 'Пока сообщений нет.'
                
        if not context_data.get('order_id'):
            await state.set_data(data={'order_id': order_id})
    else:
        new_message = event.text
        order_id = context_data.get('order_id')
        send_chat_message('CONTRACTOR', order_id, new_message)
        reply_text = f'Сообщение добавлено.\n{get_order_chat(order_id, "CONTRACTOR")}'

    markup = types.InlineKeyboardMarkup(row_width=4, resize_keyboard=True)
    back_button_cb = order_cb.new(
        order_list='history',
        list_page=1,
        order_id=order_id,
        status=get_order(order_id)['status']
    )
    new_message_cb = order_chat_cb.new(
        order_id=order_id,
        action='write'
    )
    markup.row(
        types.InlineKeyboardButton(text='Назад', callback_data=back_button_cb),
        types.InlineKeyboardButton(text='Новое сообщение', callback_data=new_message_cb)
    )

    if isinstance(event, types.callback_query.CallbackQuery):
        await event.message.edit_text(reply_text, reply_markup=markup)
    else:
        await event.answer(reply_text, reply_markup=markup)


@dp.callback_query_handler(order_chat_cb.filter(action='write'), state=ContractorUI.order_editing)
async def write_chat_message(callback: types.CallbackQuery, state: FSMContext):
    callback_data = order_chat_cb.parse(callback.data)

    reply_text = 'Введите ваше сообщение, как в обычном чате.'

    markup = types.InlineKeyboardMarkup(row_width=4, resize_keyboard=True)
    back_button_cb = order_chat_cb.new(
        order_id=callback_data['order_id'],
        action='view'
    )
    markup.add(types.InlineKeyboardButton(text='Назад', callback_data=back_button_cb))

    await callback.message.edit_text(reply_text, reply_markup=markup)


executor.start_polling(dp, skip_updates=True)

#if __name__ == '__main__':

    #dispatcher.register_message_handler(send_main_menu, commands=['menu'], state='*')
    #dispatcher.register_callback_query_handler(send_main_menu, text='menu', state='*')
    #dispatcher.register_callback_query_handler(show_order_history, navigation_cb.filter(order_list=['new', 'history']), state=ContractorUI.orders_list)
    #dispatcher.register_message_handler(show_order_history, state=ContractorUI.orders_list)
    #dispatcher.register_callback_query_handler(show_order_details, order_cb.filter(), state='*')
    #dispatcher.register_callback_query_handler(show_order_chat, order_chat_cb.filter(action='view'), state='*')
    #dispatcher.register_message_handler(show_order_chat, state=ContractorUI.order_editing)
    #dispatcher.register_callback_query_handler(write_chat_message, order_chat_cb.filter(action='write'), state=ContractorUI.order_editing)

    #executor.start_polling(dp, skip_updates=True)
