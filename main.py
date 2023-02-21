import logging, sqlite3
from aiogram import Bot, Dispatcher, executor, types
import markups as navi

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

curr_tariff = None
chat_contractor_id = None
order_find = []
orders_base = []

order_name = None
order_description = None

client_id = None
history_orders_list = []


API_TOKEN = "5821650828:AAFrGPQ6RdvPc-K76Chz40lV9n9qa72N6vM"
db_file = "db.sqlite3"
storage = MemoryStorage()


class Form(StatesGroup):
    ord_name = State()
    desc_name = State()


# --- Inline Buttons Builder ---

def gen_markup(texts: list, prefix: str, row_width: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=row_width, resize_keyboard=True)
    for num, text in enumerate(texts):
        markup.insert(InlineKeyboardButton(f"{text}", callback_data=f"{prefix}:{num}"))
        #callback_data=f"{prefix}:{num}
    return markup


# --- DB connect ---

def create_connection(db_file):
    db_connect = None
    try:
        db_connect = sqlite3.connect(db_file)
        print('DB Connected')
    except Exception as error:
        print("DB is not available, experiencing the following issue: ", str(error))

    return db_connect


def check_role(db_connect, tg_id):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur_conn = db_connect.cursor()
    clients = cur_conn.execute("SELECT * FROM telegram_bot_client")

    cur_contractor = db_connect.cursor()
    contractors = cur_contractor.execute("SELECT * FROM telegram_bot_contractor")

    cur_order = db_connect.cursor()
    orders = cur_order.execute("SELECT * FROM telegram_bot_order")

    all_clients = clients.fetchall()
    all_contractors = contractors.fetchall()
    all_orders = orders.fetchall()

    print('all_orders: ', all_orders)

    client = None
    contractor = None
    it_is_a_client = 'CLIENT CONFIRMED'
    it_is_a_contractor = 'CONTRACTOR CONFIRMED'
    send_to_register = 'PLEASE REGISTER'

    for client in all_clients:
        if int(tg_id) == client[3]:
            print('>>>>> MF is a client')
            client = client
            print('client info', client)
            return it_is_a_client, client, all_orders

    for contractor in all_contractors:
        if int(tg_id) == contractor[2]:
                    print('>>>>> MF is a contractor')
                    contractor = contractor
                    return it_is_a_contractor, contractor, all_orders
        else:
            print('>>>>> Dont know this MF')
            return send_to_register, contractor, all_orders


# Initialize DB
db_connect = create_connection(db_file)
#check_role(db_connect, tg_id)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    #await bot.send_message(message.from_user.id, f'Here is your id {message.from_user.id}')
    try:
        tg_id = message.from_user.id
        global orders_base
        res, who_is_user, orders_base = check_role(db_connect, tg_id)

        if res == 'CLIENT CONFIRMED':
            global curr_tariff
            curr_tariff = who_is_user[1]
            await bot.send_message(message.from_user.id, "Привет, {0.first_name}!\nС возвращением, Вы авторизованы как клиент.\nВаш текущий тариф: {1}\nКол-во доступных заказов в этом периоде: orders_qty ".format(message.from_user, who_is_user[1]), reply_markup = navi.client_main_menu)
        elif res == 'CONTRACTOR CONFIRMED':
            await bot.send_message(message.from_user.id, "Привет, {0.first_name}!\nС возвращением, Вы авторизованы как подрядчик.\n".format(message.from_user), reply_markup = navi.contractor_main_menu)
    except:
        await bot.send_message(message.from_user.id, "Привет, {0.first_name}!\nЯ - бот PHPService, помогу заказать небольшие фичи для Вашего сайта, давайте зарегистрируемся?".format(message.from_user), reply_markup = navi.main_menu)


@dp.message_handler(content_types=['text'])
async def bot_message(message: types.Message):
    """
    This handler will be called when user sends a message
    """
    if message.text == 'Новый клиент':
        await bot.send_message(message.from_user.id, f"Новый клиент хочет зарегаццо", reply_markup = navi.client_main_menu)

    elif message.text == 'Новая заявка':
        await bot.send_message(message.from_user.id, f"Создаем новую работу", reply_markup = navi.place_new_order_menu)

    elif message.text == 'Contractor Confirmed Main Menu':
        await bot.send_message(message.from_user.id, f"Главное меню фрилансера", reply_markup = navi.contractor_main_menu)


    elif message.text == 'Название работы':
        #await bot.send_message(message.from_user.id, f"Отправьте в чат название работы, затем нажмите кнопку подтвердить внизу", reply_markup = navi.test_one_menu)
        await Form.ord_name.set()
        await message.reply("Отправьте в чат название работы, затем нажмите кнопку подтвердить внизу", reply_markup = navi.order_name_set_menu)


        # You can use state='*' if you want to handle all states
        @dp.message_handler(state='*', commands=['cancel'])
        async def cancel_handler(message: types.Message, state: FSMContext):
            """Allow user to cancel action via /cancel command"""

            current_state = await state.get_state()
            if current_state is None:
                # User is not in any state, ignoring
                return

            # Cancel state and inform user about it
            await state.finish()
            await message.reply('Cancelled.')

        @dp.message_handler(state=Form.ord_name)
        async def process_name(message: types.Message, state: FSMContext):
            """Process user name"""

            # Finish our conversation
            await state.finish()
            await message.reply(f"Название Вашей работы: {message.text}")  # <-- Here we get the name
            global order_name
            # HERE WE HAVE THE ORDER NAME
            order_name = message.text
            print('order_name: ', order_name)

    elif message.text == 'Подтвердить название работы':
        await bot.send_message(message.from_user.id, f"...loading...", reply_markup = navi.place_new_order_menu)


    elif message.text == 'Описание работы':
        #await bot.send_message(message.from_user.id, f"Отправьте в чат название работы, затем нажмите кнопку подтвердить внизу", reply_markup = navi.test_one_menu)
        await Form.desc_name.set()
        await message.reply("Отправьте в чат описание работы, затем нажмите кнопку подтвердить внизу", reply_markup = navi.order_desc_set_menu)


        # You can use state='*' if you want to handle all states
        @dp.message_handler(state='*', commands=['cancel'])
        async def cancel_handler(message: types.Message, state: FSMContext):
            """Allow user to cancel action via /cancel command"""

            current_state = await state.get_state()
            if current_state is None:
                # User is not in any state, ignoring
                return

            # Cancel state and inform user about it
            await state.finish()
            await message.reply('Cancelled.')

        @dp.message_handler(state=Form.desc_name)
        async def process_name(message: types.Message, state: FSMContext):
            """Process user name"""

            # Finish our conversation
            await state.finish()
            await message.reply(f"Описание Вашего заказа: {message.text}")  # <-- Here we get the name
            global order_description
            # HERE WE HAVE THE ORDER DESCRIPTION
            order_description = message.text
            print('order_description: ', order_description)

    elif message.text == 'Подтвердить описание работы':
        await bot.send_message(message.from_user.id, f"...loading...", reply_markup = navi.place_new_order_menu)


    elif message.text == 'Разместить работу':

        print(order_name, order_description)

        if order_name and order_description:
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!WOW THIS SHIT WORKS!!!!!!!!!!!!!!!!!!!!')
            # !!!!!!!!!!!!!!!!!    INSERT UPDATE BD WITH ORDER INFO HERE   !!!!!!!!!!!!!!!!!!!!!!!!!

            cur_conn = db_connect.cursor()
            cur_conn.execute('''INSERT INTO telegram_bot_order(title, description, registered_at, client_id) VALUES(?,?,?,?)''', (order_name, order_description, datetime.today().strftime('%Y-%m-%d %H:%M:%S'), message.from_user.id))
            db_connect.commit()

            await bot.send_message(message.from_user.id, f"Ваша работа размещена.\nНазвание работы: {order_name}\nОписание работы: {order_description}", reply_markup = navi.client_main_menu)

        else:
            await bot.send_message(message.from_user.id, f"Пожалуйста, введите и подтвердите название и описание работы.", reply_markup = navi.place_new_order_menu)

        #await bot.send_message(message.from_user.id, f"Ваша работа размещена.\nНазвание работы: {order_name}\nОписание работы: {order_description}", reply_markup = navi.client_main_menu)

# --- HISTORY BLOCK ---

    elif message.text == 'Мои размещенные заказы':
        orders_list = []
        cur_conn = db_connect.cursor()
        clients = cur_conn.execute("SELECT * FROM telegram_bot_client")

        cur_order = db_connect.cursor()
        orders = cur_order.execute("SELECT * FROM telegram_bot_order")
        
        cur_contractor = db_connect.cursor()
        contractors = cur_contractor.execute("SELECT * FROM telegram_bot_contractor")

        all_clients = clients.fetchall()
        all_orders = orders.fetchall()
        print(all_orders)
        all_contractors = contractors.fetchall()

        for client in all_clients:
            if client[3] == message.from_user.id:
                client = list(client)
                global client_id
                client_id = client[3]

        for order in all_orders:
            print('order[4]', order[4])
            print('client_id', client_id)
            if order[4] == client_id:
                print('order', order)
                orders_list.append(order)
                print(orders_list)

        if len(orders_list) == 0:
            await bot.send_message(message.from_user.id, "Нет истории заказов. Назад в меню клиента", reply_markup = navi.client_main_menu)

        else:
            for order in orders_list:
                order_display = {"#": order[0],\
                    "Наименование работы": order[1],\
                    "Описание работы": order[2],\
                    "Дата создания работы": order[3],\
                    "Исполнитель": order[5]}
                markup = InlineKeyboardMarkup(row_width=1, resize_keyboard=True)

                global chat_contractor_id
                chat_contractor_id = order[0]

                markup.insert(InlineKeyboardButton(f"Чат с исполнителем", callback_data=f"chat_with_contractor"))

                await bot.send_message(message.from_user.id, order_display, reply_markup=markup)
                #await bot.send_message(message.from_user.id, message.text)
            print(order_find)

    elif message.text == 'Тех поддержка':
        await bot.send_message(message.from_user.id, f"Напишите @PHP_Service_Tech_Support")
        await message.reply('/help')


# Определение нового клиента и начало регистрации

    elif message.text == 'Регистрация нового клиента':

        markup = types.InlineKeyboardMarkup()

        btn_vip = types.InlineKeyboardButton(text="VIP Pack", callback_data="vip_picked")
        btn_eco = types.InlineKeyboardButton(text="Economy Pack", callback_data="eco_picked")
        btn_std = types.InlineKeyboardButton(text="Standard Pack", callback_data="std_picked")
        
        markup.add(btn_vip, btn_eco, btn_std)

        await bot.send_message(message.from_user.id, 'Economy Pack: до 5 заявок в месяц на помощь, по заявке ответят в течение суток.')
        await bot.send_message(message.from_user.id, 'Standard Pack: до 15 заявок в месяц, возможность закрепить подрядчика за собой, заявка будет рассмотрена в течение часа.')
        await bot.send_message(message.from_user.id, 'VIP Pack: до 60 заявок в месяц, возможность увидеть контакты подрядчика, заявка будет рассмотрена в течение часа.')

        await bot.send_message(message.from_user.id,
                                    f"Choose your tariff: ",
                                    reply_markup=markup)

    #если бот не узнает команду:
    else:
        await message.reply('Извините, бот не знает такую команду')



#@dp.callback_query_handler(text=["Регистрация нового фрилансера"])
#async def contractor_registration(message: types.Message):


@dp.callback_query_handler(text=["vip_picked"])
async def chat_contractor(message: types.Message):
    
    markup = types.InlineKeyboardMarkup()
    btn_finish_reg = types.InlineKeyboardButton(text="Finish Reg", callback_data="ok_to_register_client")
    markup.add(btn_finish_reg)

    await bot.send_message(message.from_user.id, f"ok", reply_markup=markup)


@dp.callback_query_handler(text=["eco_picked"])
async def chat_contractor(message: types.Message):
    pass
#send to payment + add to db


@dp.callback_query_handler(text=["std_picked"])
async def chat_contractor(message: types.Message):
    pass
#send to payment + add to db






# REGISTER PART HERE _____________________________________

@dp.callback_query_handler(text=["ok_to_register_client"])
async def chat_contractor(message: types.Message):
    tariff = 'VIP'
    fullname = f'{message.from_user.first_name} + {message.from_user.last_name}'
    telegram_id = message.from_user.id
    telegram_username = message.from_user.username

    cur_conn = db_connect.cursor()
    cur_conn.execute('''INSERT INTO telegram_bot_client(tariff, full_name, telegram_id, telegram_username) VALUES(?,?,?,?)''', (tariff, fullname, telegram_id, telegram_username))
    db_connect.commit()
    
    await bot.send_message(message.from_user.id, f"You are registered now.", reply_markup = navi.client_main_menu)


@dp.callback_query_handler(text=["chat_with_contractor"])
async def chat_contractor(message: types.Message):
    # chat_contractor_id  - это sn заказа
    # сделать логику поиска SN заказа в БД
    # и достать chat id
    if curr_tariff == 'VIP':
        telegram_username = 'insaneartillery' # взять username из БД с заказами
        print(chat_contractor_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Переходим в чат с исполнителем', url=f'https://t.me/{telegram_username}'))
        #  выше добавлять в адрес данные из БД с линком на ТГ ------------------------------------------^^^^^
        await bot.send_message(message.from_user.id,
                                f"...loading...",
                                reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Только для VIP'))
        await bot.send_message(message.from_user.id,
                                f"...loading...",
                                reply_markup=markup)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
