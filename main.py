import telebot
from telebot.apihelper import ApiException

import config
import json
import time
import calendar
# from datetime import datetime
from telebot import types

bot = telebot.TeleBot(config.TOKEN)
# time.altzone = -10800  Смещение на часовой пояс GMT +3

GREEN_CIRCLE = "🟢"
RED_CIRCLE = "🔴"

# adm_functions = ['Вакансии', 'Черный список', 'Установить частоту оповещений', 'Рассылка', 'Провести опрос']
adm_functions = ['Вакансии', 'Черный список', 'Просмотреть Базу Данных', 'Отправить сообщение-вопрос', 'Рассылка']
vacancy_functions = ["Добавить вакансию", "Удалить вакансию", "Просмотреть текущий список вакансий"]
black_list_functions = ['Добавить пользователя в черный список', 'Удалить пользователя из черного списка',
                        'Просмотреть черный список']
booking = {}
black_id = []
admin_id = 1064282294

with open("black_list.json", "r", encoding="UTF-8") as black_list:
    black_data = json.loads(black_list.read())
    for user in black_data:
        black_id.append(user)


@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == admin_id:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for function in adm_functions:
            item = types.KeyboardButton(function)
            markup.add(item)
        markup.add(types.KeyboardButton("Назад ➤"))
        sent = bot.send_message(message.chat.id, "Что бы Вы хотели сделать?", reply_markup=markup)
        bot.register_next_step_handler(sent, admin_after)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("Записаться")
        markup.add(item)
        bot.send_message(message.chat.id, "У Вас недостаточно прав для использования этой функции.",
                         reply_markup=markup)


# admin_after

# def admin_after(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     item = types.KeyboardButton("Записаться")
#     markup.add(item)
#     if message.from_user.id == admin_id:
#         if message.text == "Рассылка":
#             sent = bot.send_message(message.chat.id, "Какое сообщение Вы хотите разослать?",
#                                     reply_markup=types.ReplyKeyboardRemove())
#             bot.register_next_step_handler(sent, mailing)
#         elif message.text == 'Черный список':
#             markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#             for function in black_list_functions:
#                 item = types.KeyboardButton(function)
#                 markup.add(item)
#             sent = bot.send_message(message.chat.id, "Что бы Вы хотели сделать?", reply_markup=markup)
#             bot.register_next_step_handler(sent, admin_after)
#         elif message.text == black_list_functions[0]:
#             sent = bot.send_message(message.chat.id,
#                                     "Введите данные пользователя, которого Вы хотите добавить в черный список: ",
#                                     reply_markup=types.ReplyKeyboardRemove())
#             bot.register_next_step_handler(sent, black_list_handler, 0)
#         elif message.text == black_list_functions[1]:
#             black_list_handler(message, 1)
#         elif message.text == black_list_functions[2]:
#             black_list_handler(message, 2)
#         elif message.text == 'Просмотреть Базу Данных':
#             show_database()
#         elif message.text == 'Отправить сообщение-вопрос':
#             markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#             item1 = types.KeyboardButton("Всем")
#             item2 = types.KeyboardButton("Выбрать пользователя")
#             markup.add(item1, item2)
#             sent = bot.send_message(message.chat.id,
#                                     "Разослать опрос всем пользователям или выбрать конкретного пользователя?",
#                                     reply_markup=markup)
#             bot.register_next_step_handler(sent, admin_after)
#         elif message.text.lower() == 'всем':
#             sent = bot.send_message(message.chat.id, "Опрос на какую тему Вы хотите провести?",
#                                     reply_markup=types.ReplyKeyboardRemove())
#             bot.register_next_step_handler(sent, mailing, arguments=True)
#         elif message.text == 'Выбрать пользователя':
#             new_message = ""
#             with open("user_base.json", "r", encoding="UTF-8") as database:
#                 data = json.loads(database.read())
#                 for s_user in data:
#                     new_message += "Имя: " + s_user['first_name'] + ", id: " + str(s_user) + ";\n"
#             bot.send_message(message.chat.id, new_message, reply_markup=types.ReplyKeyboardRemove())
#             sent = bot.send_message(message.chat.id, "Выберите желаемого пользователя и отправьте его id",
#                                     reply_markup=types.ReplyKeyboardRemove())
#             bot.register_next_step_handler(sent, q_user)
#         elif message.text == "Назад ➤":
#             bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
#     else:
#         bot.send_message(message.chat.id, "У Вас недостаточно прав для использования этой функции.",
#                          reply_markup=markup)


# @bot.message_handler(commands=['start'], func=lambda message: message.chat.id not in black_id)
# def start(message):
#     chat(message)


def create_calendar(month_diff=0):
    red_border = {"y": time.strftime("%Y"),
                  "m": time.strftime("%m"),
                  "d": [time.strftime("%d"), time.strftime("%a")]}
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь",
              "Декабрь"]

    # INT
    month = int(red_border["m"]) + month_diff if int(red_border["m"]) + month_diff < 13 else int(
        red_border["m"]) + month_diff - 12
    year = int(red_border["y"]) + 1 if int(red_border["m"]) + month_diff > 12 else int(red_border["y"])

    # STR
    new_month = str(month + 1) if month != 12 else "1"
    new_year = str(year + 1) if new_month == "1" else str(year)

    prev_month = str(month - 1) if month != 1 else "12"
    prev_year = str(year - 1) if prev_month == "12" else str(year)

    keyboard = [[types.InlineKeyboardButton("<", callback_data="move=" + str(month_diff - 1)),
                 types.InlineKeyboardButton(months[month - 1], callback_data="-2"),
                 types.InlineKeyboardButton(">", callback_data="move=" + str(month_diff + 1))]]
    name_line = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
    second_line, keyboard_row = [], []
    for day_name in name_line:
        second_line.append(types.InlineKeyboardButton(day_name, callback_data="-2"))
    keyboard.append(second_line)

    first_day = calendar.monthrange(year, month)[0]
    # Зачем это... Есть же уже -_- Хм. Надо убрать~
    number_prev_month = month - 1 if month != 1 else 12
    year_prev_month = year if number_prev_month != 12 else year - 1
    # ---------------------------------------------
    prev_month_days = calendar.monthrange(year_prev_month, number_prev_month)[1]
    days = int(calendar.monthrange(year, month)[1])

    filename = "datebase.json"
    with open(filename, "r", encoding="UTF-8") as datebase:
        data = json.loads(datebase.read())
        if first_day != 0:
            numbers = range(prev_month_days, prev_month_days - first_day, -1).__reversed__()
            for num in numbers:
                if month_diff > 0:
                    prev_date = str(num) + "." + prev_month + "." + prev_year
                    value = prev_date
                    if prev_date not in data:
                        color_circle = GREEN_CIRCLE
                        if (config.day_border[0][1] == 0 and config.day_border[1][1] == 0) or (
                                config.day_border[0][1] == 30 and config.day_border[1][1] == 30):
                            amount = [config.day_border[1][0] - config.day_border[0][0], 0]
                        elif config.day_border[0][1] == 0 and config.day_border[1][1] == 30:
                            amount = [config.day_border[1][0] - config.day_border[0][0], 30]
                        elif config.day_border[0][1] == 30 and config.day_border[1][1] == 0:
                            amount = [config.day_border[1][0] - config.day_border[0][0] - 1, 30]
                        data[prev_date] = {}
                        for i in range(amount[0] * 2 + int(amount[1] / 30)):
                            new_minutes = config.day_border[0][1] + i * 30
                            if new_minutes % 60 == 0:
                                new_hour = str(config.day_border[0][0] + new_minutes // 60)
                                new_minutes = "00"
                            elif new_minutes % 30 == 0:
                                new_hour = str(config.day_border[0][0] + new_minutes // 60)
                                new_minutes = "30"
                            if len(new_hour) < 2:
                                new_hour = "0" + new_hour
                            data[prev_date][new_hour + ":" + new_minutes] = []  # [id, type]
                        write_database(data, filename)
                    else:
                        available = False
                        for shift in data[prev_date]:
                            if not data[prev_date][shift]:
                                available = True
                        if available:
                            color_circle = GREEN_CIRCLE
                        else:
                            color_circle = RED_CIRCLE
                            value = "-1"
                else:
                    color_circle = RED_CIRCLE
                    value = "-1"
                keyboard_row.append(types.InlineKeyboardButton(color_circle + str(num), callback_data=value))
            del numbers

        for day in range(days):
            formatted_date = str(day + 1) + "." + str(month) + "." + str(year)
            value = "0" \
                if day + 1 <= int(red_border["d"][0]) and month == int(red_border["m"]) \
                   or month < int(red_border["m"]) \
                else formatted_date
            if month_diff < 0:
                color_circle = RED_CIRCLE
            else:
                if day < int(red_border["d"][0]) and month_diff == 0:
                    color_circle = RED_CIRCLE
                    value = "-1"
                elif formatted_date not in data:
                    color_circle = GREEN_CIRCLE

                    if (config.day_border[0][1] == 0 and config.day_border[1][1] == 0) or (
                            config.day_border[0][1] == 30 and config.day_border[1][1] == 30):
                        amount = [config.day_border[1][0] - config.day_border[0][0], 0]
                    elif config.day_border[0][1] == 0 and config.day_border[1][1] == 30:
                        amount = [config.day_border[1][0] - config.day_border[0][0], 30]
                    elif config.day_border[0][1] == 30 and config.day_border[1][1] == 0:
                        amount = [config.day_border[1][0] - config.day_border[0][0] - 1, 30]
                    data[formatted_date] = {}
                    for i in range(amount[0] * 2 + int(amount[1] / 30)):
                        new_minutes = config.day_border[0][1] + i * 30
                        if new_minutes % 60 == 0:
                            new_hour = str(config.day_border[0][0] + new_minutes // 60)
                            new_minutes = "00"
                        elif new_minutes % 30 == 0:
                            new_hour = str(config.day_border[0][0] + new_minutes // 60)
                            new_minutes = "30"
                        if len(new_hour) < 2:
                            new_hour = "0" + new_hour
                        data[formatted_date][new_hour + ":" + new_minutes] = []  # [id, type]
                    write_database(data, filename)
                else:
                    available = False
                    for shift in data[formatted_date]:
                        if not data[formatted_date][shift]:
                            available = True
                    if available:
                        color_circle = GREEN_CIRCLE
                    else:
                        color_circle = RED_CIRCLE
                        value = "-1"

            new_button = types.InlineKeyboardButton(color_circle + str(day + 1), callback_data=str(value))
            keyboard_row.append(new_button)
            if len(keyboard_row) == 7:
                keyboard.append(keyboard_row)
                keyboard_row = []
        i = 1
        if len(keyboard_row) != 0:
            while len(keyboard_row) < 7:
                if month_diff >= 0:
                    post_date = str(i) + "." + new_month + "." + new_year
                    value = post_date
                    if post_date not in data:
                        color_circle = GREEN_CIRCLE
                        if (config.day_border[0][1] == 0 and config.day_border[1][1] == 0) or (
                                config.day_border[0][1] == 30 and config.day_border[1][1] == 30):
                            amount = [config.day_border[1][0] - config.day_border[0][0], 0]
                        elif config.day_border[0][1] == 0 and config.day_border[1][1] == 30:
                            amount = [config.day_border[1][0] - config.day_border[0][0], 30]
                        elif config.day_border[0][1] == 30 and config.day_border[1][1] == 0:
                            amount = [config.day_border[1][0] - config.day_border[0][0] - 1, 30]
                        data[post_date] = {}
                        for j in range(amount[0] * 2 + int(amount[1] / 30)):
                            new_minutes = config.day_border[0][1] + j * 30
                            if new_minutes % 60 == 0:
                                new_hour = str(config.day_border[0][0] + new_minutes // 60)
                                new_minutes = "00"
                            elif new_minutes % 30 == 0:
                                new_hour = str(config.day_border[0][0] + new_minutes // 60)
                                new_minutes = "30"
                            if len(new_hour) < 2:
                                new_hour = "0" + new_hour
                            data[post_date][new_hour + ":" + new_minutes] = []  # [id, type]
                        write_database(data, filename)
                    else:
                        available = False
                        for shift in data[post_date]:
                            if not data[post_date][shift]:
                                available = True
                        if available:
                            color_circle = GREEN_CIRCLE
                        else:
                            color_circle = RED_CIRCLE
                            value = "-1"
                else:
                    color_circle = RED_CIRCLE
                    value = "-1"

                keyboard_row.append(
                    types.InlineKeyboardButton(color_circle + str(i), callback_data=value))
                i += 1
            keyboard.append(keyboard_row)
    inline_keyboard = types.InlineKeyboardMarkup(keyboard)
    return inline_keyboard


@bot.message_handler(content_types=['text'], func=lambda message: message.chat.id not in black_id)
def chat(message):
    initialisation(message)
    if message.chat.type == 'private':
        if message.text.lower() == 'привет' or message.text.lower() == 'записаться' or message.text == '/start':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Консультация")
            item2 = types.KeyboardButton("Тренировка")
            item3 = types.KeyboardButton("Тейпирование")
            # Тут бы подробнее о каждом расписать, чтобы человек понимал. Имхо.
            markup.add(item1, item2, item3)
            global booking
            sent = bot.send_message(message.chat.id,
                                    "Привет, <b>{0.first_name}</b>!\nЯ бот-помощник Fitandbaby. Я помогу тебе выбрать и записаться на услугу от Fitandbaby.\nДля начала, выберите услугу из предложенных".format(
                                        message.from_user), parse_mode='html', reply_markup=markup)
            bot.register_next_step_handler(sent, choose_category)


def choose_category(message):
    global booking
    if message.text.lower() == "консультация" or message.text.lower() == "тренировка":
        booking['category'] = message.text

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Очная")
        item2 = types.KeyboardButton("Онлайн")
        markup.add(item1, item2)

        sent = bot.send_message(message.chat.id,
                                'Выбери тип проведения услуги "Очная" или "Онлайн"', reply_markup=markup)
        bot.register_next_step_handler(sent, choose_type)
    elif message.text.lower() == "тейпирование":
        booking['category'] = message.text
        booking['type'] = "Очная"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("Отправить текущее местоположение", request_location=True)
        markup.add(item)

        bot.send_message(message.chat.id, "Принято.")
        sent = bot.send_message(message.chat.id,
                                'Укажите Ваш адрес, где будет проходить консультация',
                                reply_markup=markup)
        bot.register_next_step_handler(sent, choose_addr)
    else:
        sent = bot.send_message(message.chat.id,
                                'Некорректный формат введенных данных, отправьте сообщение с одним словом "Консультация", "Тренировка" либо "Тейпирование"')
        bot.register_next_step_handler(sent, choose_category)


def choose_type(message):
    global booking
    if message.text.lower() == "очная":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("Отправить текущее местоположение", request_location=True)
        markup.add(item)

        booking['type'] = message.text
        bot.send_message(message.chat.id, "Принято.")

        sent = bot.send_message(message.chat.id,
                                'Укажите Ваш адрес, где будет проходить консультация',
                                reply_markup=markup)
        # 'Укажите Ваш адрес, где будет проходить консультация\nМожете записать адрес текстом либо отправить местоположение, нажав на кнопку "Отправить текущее местоположение"',
        bot.register_next_step_handler(sent, choose_addr)
    elif message.text.lower() == "онлайн":
        booking['type'] = message.text
        booking['addr'] = None
        bot.send_message(message.chat.id, "Принято.")

        sent = bot.send_message(message.chat.id, "Отправьте свой логин в Instagram для связи",
                                reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(sent, choose_contact)
    else:
        sent = bot.send_message(message.chat.id,
                                'Некорректный формат введенных данных, отправьте сообщение с одним словом "Очная" либо "Онлайн"')
        bot.register_next_step_handler(sent, choose_type)


def choose_addr(message):
    global booking
    booking['addr'] = message.text
    bot.send_message(message.chat.id, "Принято.")
    sent = bot.send_message(message.chat.id, "Отправьте свой логин в Instagram для связи",
                            reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(sent, choose_contact)

    # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # item1 = types.KeyboardButton("Да, отправить")
    # item2 = types.KeyboardButton("Нет")
    # markup.add(item1, item2)
    # message = "Тип консультации: " + booking['type'] + "\nДата консультации: " + booking['date'] + \
    #           "\nВремя консультации: " + booking['time'] + "\nАдрес: " + booking['addr']
    # bot.send_message(message.chat.id, message)
    # sent = bot.send_message(message.chat.id, "Готово.\n\n" + message + "\n\nОтправить заявку?", reply_markup=markup)
    # bot.register_next_step_handler(sent, )


def choose_contact(message):
    global booking
    booking['contact'] = message.text
    inline_keyboard = create_calendar()
    bot.send_message(message.chat.id, "Выберите дату консультации >", reply_markup=inline_keyboard)


# def choose_date(message):
#     global booking
#     # Допустим, что дата подается в верном формате, например, через callback-query selector
#     booking['date'] = message.text
#     bot.send_message(message.chat.id, "Принято.")
#     sent = bot.send_message(message.chat.id, "Выберите время консультации")
#     bot.register_next_step_handler(sent, choose_time)


# def choose_time(message):
#     # Допустим, что время подается в верном формате, например, через callback-query selector
#     booking['time'] = message.text
#     bot.send_message(message.chat.id, "Принято.")
#     if booking['type'] == "Очная":
#         markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         item = types.KeyboardButton(text="Отправить мое местоположение", request_location=True)
#         markup.add(item)
#         sent = bot.send_message(message.chat.id, "Укажите Ваш адрес, где будет проходить консультация")
#         bot.register_next_step_handler(sent, choose_addr, booking)
#     else:
#         booking['addr'] = None


@bot.callback_query_handler(func=lambda call: True)
def date_callback_handler(call):
    global booking
    if call.data == "0":
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                  text='Выберите день не из тех, что прошли или сегодня')
    elif call.data == "-1":
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                  text="Этот день полностью занят, выберите другой")
    elif call.data == "-2":
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=None)
    elif call.data == "go_back":
        inline_keyboard = create_calendar()
        bot.edit_message_text(
            "Выберите дату консультации >",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=inline_keyboard
        )
    elif call.data == "change_data":
        # Изменяет сообщение на выбор даты и дальше идет по порядку. Но не удаляет запись пользователя.
        inline_keyboard = create_calendar()
        bot.edit_message_text(
            "Выберите дату консультации > ",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=inline_keyboard
        )
    elif call.data == "cancel":
        filename = "datebase.json"
        with open(filename, "r", encoding="UTF-8") as database:
            data = json.loads(database.read())
            data[booking['date']] = []
            write_database(data, filename)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton("Записаться")
            markup.add(item)
            bot.send_message(call.message.chat.id, "Ваша запись успешно отменена.", reply_markup=markup)
    # При нажатии кнопки "<" или ">"
    elif "move" in call.data:
        month_diff = int(call.data[5:])
        if abs(month_diff) <= 3:
            inline_keyboard = create_calendar(month_diff)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=inline_keyboard)
    # При нажатии на кнопку со временем
    elif "time" in call.data:
        filename = "datebase.json"
        with open(filename, "r", encoding="UTF-8") as datebase:
            data = json.loads(datebase.read())
            if data[booking["date"]][call.data[5:]]:
                bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                          text='Это время уже занято, выберите другое')
            else:
                this_hour = call.data[5:7]
                this_minutes = call.data[8:10]
                start_hour = this_hour
                start_minutes = this_minutes

                # Запись информации в БД на первые полчаса
                data[booking["date"]][call.data[5:]] = [call.from_user.id, {
                    'type': booking['type'],
                    'category': booking['category'],
                    'contact': booking['contact'],
                    'addr': booking['addr'],
                    'is_start_time': True
                }]
                # Запись информации в БД на вторые полчаса, если это не тейпирование
                if booking['category'].lower() != "тейпирование":
                    next_half_hour = this_hour + ":30" if this_minutes == "00" else str(int(this_hour) + 1) + ":00"
                    try:
                        data_booking_next_half_hour = data[booking["date"]][next_half_hour]
                    except KeyError:
                        data_booking_next_half_hour = "Error"
                    if data_booking_next_half_hour:
                        bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                                  text=booking['category'].capitalize() +
                                                       ' занимает более получаса времени, выберите другое время из доступного')
                        return
                    data[booking["date"]][next_half_hour] = [call.from_user.id, {
                        'type': booking['type'],
                        'category': booking['category'],
                        'contact': booking['contact'],
                        'addr': booking['addr']
                    }]

                    this_hour = next_half_hour[:2]
                    this_minutes = next_half_hour[3:]

                if booking['type'].lower() == "очная":
                    # Проверка, не является ли выбранная дата нижней границей по времени
                    if call.data[5:] != str(config.day_border[0][0]) + ":" + str(config.day_border[0][1]):
                        prev_half_hour = str(
                            int(start_hour) - 1) + ":30" if start_minutes == "00" else start_hour + ":00"
                        # Проверка, занят ли предшествующий получасовой интервал
                        if data[booking["date"]][prev_half_hour]:
                            if data[booking["date"]][prev_half_hour][1]['type'].lower() == "онлайн":
                                bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                                          text='Выбранные Вами полчаса потребуются на перемещение от предыдущего клиента. Пожалуйста, выберите другое время')
                                return
                        data[booking["date"]][prev_half_hour] = [call.from_user.id, {
                            'type': booking['type'],
                            'category': booking['category'],
                            'contact': booking['contact'],
                            'addr': booking['addr']
                        }]
                    next_half_hour = this_hour + ":30" if this_minutes == "00" else str(int(this_hour) + 1) + ":00"
                    if next_half_hour != str(config.day_border[1][0]) + ":" + str(config.day_border[1][1]):
                        if data[booking["date"]][next_half_hour]:
                            if data[booking["date"]][next_half_hour][1]['type'].lower() == "онлайн":
                                bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                                          text='На дальнейшее время уже записан клиент, чтобы добраться к которому потребуются дополнительные полчаса после Вас. Пожалуйста, выберите время ранее или позже из доступного')
                                return
                        data[booking["date"]][next_half_hour] = [call.from_user.id, {
                            'type': booking['type'],
                            'category': booking['category'],
                            'contact': booking['contact'],
                            'addr': booking['addr']
                        }]

                write_database(data, filename)

                # Сделать подтверждение ->
                inline_keyboard = telebot.types.InlineKeyboardMarkup()
                inline_keyboard.row(types.InlineKeyboardButton("Изменить дату", callback_data="change_date"),
                                    types.InlineKeyboardButton("Отменить запись", callback_data="cancel"))

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item = types.KeyboardButton("Записаться")
                markup.add(item)

                type_category_msg = booking['type'].capitalize() + " " + booking['category'] if \
                    booking['category'].lower() != "тейпирование" else "Тейпирование"
                addr_msg = '\n-> Адрес: ' + booking['addr'] if booking['addr'] is not None else ""

                bot.send_message(admin_id, 'Пользователь ' + call.from_user.first_name + ' записался на\n-> "'
                                 + type_category_msg + '",\n-> ' + booking['date']
                                 + '\n-> Время: ' + call.data[5:] + '\n-> Instagram: ' + booking['contact']
                                 + addr_msg)

                bot.edit_message_text(
                    'Вы успешно записались\n-> "' + type_category_msg +
                    '",\n-> ' + booking['date'] +
                    '\n-> Время: ' + call.data[5:],
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=inline_keyboard
                )
                bot.send_message(call.message.chat.id,
                                 'Если хотите записаться на новую услугу, напишите "Записаться" или нажмите на соответствующую кнопку',
                                 reply_markup=markup)
                booking = {}
    # При нажатии кнопки даты
    else:
        booking["date"] = call.data
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                  text='Принято')
        with open("datebase.json", "r", encoding="UTF-8") as datebase:
            data = json.loads(datebase.read())
            keyboard, inner_keyboard = [], []
            for time_shift in data[call.data]:
                color_circle = GREEN_CIRCLE + " "
                if data[call.data][time_shift]:
                    color_circle = RED_CIRCLE + " "
                shift = time_shift[:2] + ":" + time_shift[3:]
                inner_keyboard.append(types.InlineKeyboardButton(color_circle + shift, callback_data="time=" + shift))
                if len(inner_keyboard) == 2:
                    keyboard.append(inner_keyboard)
                    inner_keyboard = []
            keyboard.append(inner_keyboard)
            keyboard.append([types.InlineKeyboardButton("< Назад", callback_data="go_back")])
            inline_keyboard = types.InlineKeyboardMarkup(keyboard)
            bot.edit_message_text(
                "Выберите время консультации.\nКонсультация занимает 1 час, тренировка - 50 минут, тейпирование - 30мин",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=inline_keyboard
            )
            # bot.send_message(call.message.chat.id, "Выберите время консультации.\nКонсультация или тренировка занимают 1 час, тейпирование - 30мин", reply_markup=inline_keyboard)
            # data[call.data] = new_day


def black_list_handler(message, direction):
    global past_black_user
    if direction == 0:
        with open("user_base.json", "r", encoding="UTF-8") as database:
            data = json.loads(database.read())
            try:
                search_param = int(message.text)
            except ValueError:
                search_param = message.text
                place = search_param.find("@")
                search_param = search_param[place + 1:]
            finally:
                i = 0
                for s_user in data['users']:
                    if s_user['id'] == search_param or s_user['username'] == search_param:
                        new_black_user = data['users'][i]
                        del data['users'][i]
                        data['items'] -= 1
                        write_database(data, "user_base.json")
                        with open("black_list.json", "r", encoding="UTF-8") as blackList:
                            data = json.loads(blackList.read())
                            black_id.append(new_black_user['id'])
                            data['users'].append(new_black_user)
                            all_data = {"items": data['items'] + 1, "users": data['users']}
                            write_database(all_data, "black_list.json")
                        bot.send_message(message.chat.id, "Сделано!", reply_markup=types.ReplyKeyboardRemove())
                        return
                    i += 1
    if message.text == "Назад ➤":
        admin(message)
        return -1
    else:
        with open("black_list.json", "r", encoding="UTF-8") as database:
            data = json.loads(database.read())
            if direction == 5:
                data['items'] = data['items'] - 1
                try:
                    obj_id = int(message.text)
                except ValueError:
                    bot.send_message(message.chat.id, "Недопустимое значение идентификатора.",
                                     reply_markup=types.ReplyKeyboardRemove())
                    return 1
                i = 0
                for obj in data['users']:
                    if obj['id'] == obj_id:
                        past_black_user = data['users'][i]
                        del data['users'][i]
                        break
                    i += 1
                write_database(data, "black_list.json")
                with open("user_base.json", "r", encoding="UTF-8") as white_list_base:
                    data = json.loads(white_list_base.read())
                    data['items'] = data['items'] + 1
                    data['users'].append(past_black_user)
                    write_database(data, "user_base.json")
                bot.send_message(message.chat.id, "Готово!", reply_markup=types.ReplyKeyboardRemove())
                return 0
            for obj in data['users']:
                bot.send_message(message.chat.id, "id: " + str(obj['id']) + ". Имя: " + obj["first_name"],
                                 reply_markup=types.ReplyKeyboardRemove())
            if direction == 1:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item = types.KeyboardButton("Назад ➤")
                markup.add(item)
                sent = bot.send_message(message.chat.id, "Выберите пользователя, которого хотите удалить (id)",
                                        reply_markup=markup)
                bot.register_next_step_handler(sent, black_list_handler, 5)
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for function in adm_functions:
                    item = types.KeyboardButton(function)
                    markup.add(item)
                item = types.KeyboardButton("Назад ➤")
                markup.add(item)
                sent = bot.send_message(message.chat.id, "Полный список доступных пользователей ↑",
                                        reply_markup=markup)
                bot.register_next_step_handler(sent, admin_after)


# mailing

# def mailing(message, arguments=None, user_id=None):
#     markup = back_markup() - Нет
#     with open("user_base.json", "r", encoding="UTF-8") as database:
#         data = json.loads(database.read())
#         if arguments:
#             if user_id is not None:
#                 try:
#                     sent = bot.send_message(user_id, message.text, reply_markup=markup)
#                     bot.register_next_step_handler(sent, feedback, message.text)
#                 except ApiException:
#                     bot.send_message(admin_id,
#                                      "Вопрос не был отправлен, т.к. пользователь заблокировал бота или отправка сообщений ему невозможна.",
#                                      reply_markup=markup)
#                 finally:
#                     return 0
#             for person in data['users']:
#                 try:
#                     if person['id'] != message.from_user.id:
#                         sent = bot.send_message(person['id'], message.text, reply_markup=markup)
#                         bot.register_next_step_handler(sent, feedback, message.text)
#                     else:
#                         bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
#                 except ApiException:
#                     continue
#                 else:
#                     continue
#             return 0
#         if message.content_type == 'text':
#             for person in data['users']:
#                 try:
#                     if person['id'] != message.from_user.id:
#                         bot.send_message(person['id'], message.text, reply_markup=markup)
#                     else:
#                         bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
#                 except ApiException:
#                     continue
#                 else:
#                     continue
#             bot.send_message(message.chat.id, "Разослано.", reply_markup=markup)
#         elif message.content_type == 'photo':
#             raw = message.photo[2].file_id
#             name = "mailing.jpg"
#             file_info = bot.get_file(raw)
#             downloaded_file = bot.download_file(file_info.file_path)
#             with open(name, "wb") as photo:
#                 photo.write(downloaded_file)
#             for person in data['users']:
#                 photo = open(name, "rb")
#                 try:
#                     if person['id'] != message.from_user.id:
#                         bot.send_photo(person['id'], photo, reply_markup=markup)
#                     else:
#                         bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
#                 except ApiException:
#                     photo.close()
#                     continue
#                 else:
#                     photo.close()
#                     continue
#             bot.send_message(message.chat.id, "Разослано.", reply_markup=markup)
#         elif message.content_type == 'document':
#             raw = message.document.file_id
#             name = "mailing" + message.document.file_name[-4:]
#             file_info = bot.get_file(raw)
#             downloaded_file = bot.download_file(file_info.file_path)
#             with open(name, "wb") as document:
#                 document.write(downloaded_file)
#             for person in data['users']:
#                 document = open(name, "rb")
#                 try:
#                     if person['id'] != message.from_user.id:
#                         bot.send_document(person['id'], document, reply_markup=markup)
#                     else:
#                         bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
#                 except ApiException:
#                     document.close()
#                     continue
#                 else:
#                     document.close()
#                     continue
#             bot.send_message(message.chat.id, "Разослано.", reply_markup=markup)
#         else:
#             bot.send_message(message.chat.id, "Неподдерживаемый тип файла", reply_markup=markup)


def feedback(message, question):
    bot.send_message(admin_id,
                     'Ответ на Ваш вопрос "' + question + '" — "' + message.text + '" от:\n(id) ' + str(
                         message.from_user.id) + ',\n(name) '
                     + str(message.from_user.first_name))
    bot.send_message(message.chat.id, "Принято.\nБлагодарим за ответ!)")


def write_database(data, filename):
    with open(filename, "w", encoding="UTF-8") as database:
        json.dump(data, database, indent=1, ensure_ascii=False, separators=(',', ':'))


def show_database():
    try:
        filename = "interviewees.json"
        with open(filename, "r", encoding="UTF-8") as database_file:
            bot.send_document(admin_id, database_file)
        filename = "vacancy.json"
        with open(filename, "r", encoding="UTF-8") as database_file:
            bot.send_document(admin_id, database_file)
        filename = "user_base.json"
        with open(filename, "r", encoding="UTF-8") as database_file:
            bot.send_document(admin_id, database_file)
        filename = "black_list.json"
        with open(filename, "r", encoding="UTF-8") as database_file:
            bot.send_document(admin_id, database_file)
    except FileNotFoundError:
        bot.send_message(admin_id, '[Ошибка] Файл БД "' + filename + '"не найден.',
                         reply_markup=types.ReplyKeyboardRemove())


def initialisation(message):
    filename = "user_base.json"
    with open(filename, "r", encoding="UTF-8") as database:
        data = json.loads(database.read())
        if message.from_user.id not in data:
            data[message.from_user.id] = {"first_name": message.from_user.first_name,
                                          "last_name": message.from_user.last_name,
                                          "username": message.from_user.username}
            write_database(data, filename)


bot.polling(none_stop=True)
