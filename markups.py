from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# KeyboardButton - экземпляр кнопки
# ReplyKeyboardMarkup - меню для бота


# --- Main Menu ---
#btn_main_menu = KeyboardButton('Главное меню')

btn_new_client = KeyboardButton('Регистрация нового клиента')
btn_new_contractor = KeyboardButton('Регистрация нового фрилансера')

btn_new_order = KeyboardButton('Новая заявка')
btn_my_placed_orders = KeyboardButton('Мои размещенные заказы')

btn_find_orders = KeyboardButton('Найти заказы')
btn_my_taken_orders = KeyboardButton('Мои принятые заказы')

btn_support = KeyboardButton('Тех поддержка')

main_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_new_client, btn_new_contractor, btn_support)
client_main_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_new_order, btn_my_placed_orders, btn_support)
contractor_main_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_find_orders, btn_my_taken_orders, btn_support)


btn_job_name = KeyboardButton('Название работы')
btn_job_desc = KeyboardButton('Описание работы')
#btn_add_file = KeyboardButton('Добавить файл')
btn_send_order = KeyboardButton('Разместить работу')

place_new_order_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_job_name, btn_job_desc, btn_send_order)

# should make an order menu with fields: Order name, Order deadline, Order Description, 
# if VIP tariff? Should attach 


btn_order_name = KeyboardButton('Подтвердить название работы')
order_name_set_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_order_name)


btn_order_desc = KeyboardButton('Подтвердить описание работы')
order_desc_set_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_order_desc)


order_placed_menu = ReplyKeyboardMarkup(resize_keyboard = True).add(btn_order_desc)
