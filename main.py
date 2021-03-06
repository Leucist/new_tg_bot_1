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
adm_functions = ['Просмотреть записи', 'Добавить выходной', 'Отправить сообщение-вопрос', 'Рассылка']
black_list_functions = ['Добавить пользователя в черный список', 'Удалить пользователя из черного списка',
                        'Просмотреть черный список']

booking = {
    "type": None,
    "category": None,
    "contact": None,
    "addr": []
}
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


def admin_after(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Записаться")
    markup.add(item)
    if message.from_user.id == admin_id:
        # В использовании message.chat.id вместо admin_id есть свой резон. Например, легче будет переоборудовать под
        # ...несколько админов, используя то же 'if message.from_user.id in admin_id' рассматривая admin_id как массив.
        if message.text.lower() == "просмотреть записи":
            sent = bot.send_message(message.chat.id,
                                    "На какой месяц Вы хотели бы просмотреть записи?\nОтвет пришлите числом в формате мм.гг (Например: 12.22)",
                                    reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(sent, check_records)
        elif message.text.lower() == "рассылка":
            sent = bot.send_message(message.chat.id, "Какое сообщение Вы хотите разослать?",
                                    reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(sent, mailing)
        elif message.text.lower() == "добавить выходной":
            sent = bot.send_message(message.chat.id, 'Отправьте дату желаемого выходного в формате "дд.мм.гггг" без нулей и четырьмя цифрами года. Т.е., например: "2.12.2022", а не "02.12.22"',
                                    reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(sent, add_holiday)
        # elif message.text == 'Черный список':
        #     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #     for function in black_list_functions:
        #         item = types.KeyboardButton(function)
        #         markup.add(item)
        #     sent = bot.send_message(message.chat.id, "Что бы Вы хотели сделать?", reply_markup=markup)
        #     bot.register_next_step_handler(sent, admin_after)
        # elif message.text == black_list_functions[0]:
        #     sent = bot.send_message(message.chat.id,
        #                             "Введите данные пользователя, которого Вы хотите добавить в черный список: ",
        #                             reply_markup=types.ReplyKeyboardRemove())
        #     bot.register_next_step_handler(sent, black_list_handler, 0)
        # elif message.text == black_list_functions[1]:
        #     black_list_handler(message, 1)
        # elif message.text == black_list_functions[2]:
        #     black_list_handler(message, 2)
        elif message.text.lower() == 'отправить сообщение-вопрос':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Всем")
            item2 = types.KeyboardButton("Выбрать пользователя")
            markup.add(item1, item2)
            sent = bot.send_message(message.chat.id,
                                    "Разослать опрос всем пользователям или выбрать конкретного пользователя?",
                                    reply_markup=markup)
            bot.register_next_step_handler(sent, admin_after)
        elif message.text.lower() == 'всем':
            sent = bot.send_message(message.chat.id, "Опрос на какую тему Вы хотите провести?",
                                    reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(sent, mailing, arguments=True)
        elif message.text.lower() == 'выбрать пользователя':
            new_message = ""
            with open("user_base.json", "r", encoding="UTF-8") as database:
                data = json.loads(database.read())
                for s_user in data:
                    new_message += "Имя: " + data[s_user]['first_name'] + ", id: " + str(s_user) + ";\n"
            bot.send_message(message.chat.id, new_message, reply_markup=types.ReplyKeyboardRemove())
            sent = bot.send_message(message.chat.id, "Выберите желаемого пользователя и отправьте его id",
                                    reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(sent, q_user)
        elif message.text == "Назад ➤":
            bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "У Вас недостаточно прав для использования этой функции.",
                         reply_markup=markup)


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
            value = "0" if day + 1 <= int(red_border["d"][0]) and month <= int(red_border["m"]) else formatted_date
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
        # if message.text.lower() == 'привет' or message.text.lower() == 'записаться' or message.text == '/start':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Консультация")
        item2 = types.KeyboardButton("Тренировка")
        item3 = types.KeyboardButton("Тейпирование")
        item4 = types.KeyboardButton("Отмена")
        markup.add(item1, item2, item3, item4)
        global booking
        booking = {}
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
    elif message.text.lower() == "отмена":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("Записаться")
        markup.add(item)
        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
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
        booking['addr'] = []
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
    if message.content_type == "location":
        booking['addr'] = ['location', message.location.latitude, message.location.longitude]
    elif message.text is not None:
        booking['addr'] = ['addr', message.text]
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("Отправить текущее местоположение", request_location=True)
        markup.add(item)
        sent = bot.send_message(message.chat.id,
                                'Ошибка, неверный формат сообщения. Попробуйте снова.\n\nУкажите Ваш адрес, где будет проходить консультация',
                                reply_markup=markup)
        bot.register_next_step_handler(sent, choose_addr)
        return 1
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
    elif call.data == "warning_change_date":
        inline_keyboard = telebot.types.InlineKeyboardMarkup()
        inline_keyboard.row(types.InlineKeyboardButton("Изменить дату", callback_data="change_date"),
                            types.InlineKeyboardButton("Отменить запись", callback_data="warning_cancel"))
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=inline_keyboard)
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                  text="Внимание! Это автоматически отменит Вашу предыдущую запись")
    elif call.data == "warning_cancel":
        inline_keyboard = telebot.types.InlineKeyboardMarkup()
        inline_keyboard.row(types.InlineKeyboardButton("Изменить дату", callback_data="warning_change_date"),
                            types.InlineKeyboardButton("Отменить запись", callback_data="cancel"))
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=inline_keyboard)
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                  text="Внимание! Это отменит Вашу запись. Нажмите снова, если хотите продолжить")
    elif call.data == "change_date":
        # Изменяет сообщение на выбор даты и дальше идет по порядку
        if booking == {"type": None, "category": None, "contact": None, "addr": []}:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                      text='Сессия была прервана и функция изменения даты для этой записи недоступна. Можете воспользоваться кнопкой "Отменить запись" и записаться заново вручную')
            return -1
        delete_record("datebase.json", call)
        inline_keyboard = create_calendar()
        bot.edit_message_text(
            "Выберите дату консультации > ",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=inline_keyboard
        )
    elif call.data == "cancel":
        delete_record("datebase.json", call)
    # При нажатии кнопки "<" или ">"
    elif "move" in call.data:
        month_diff = int(call.data[5:])
        if abs(month_diff) <= 3:
            inline_keyboard = create_calendar(month_diff)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=inline_keyboard)
    # При нажатии на кнопку со временем
    elif "time" in call.data:
        # Проверка, пустое booking или нет. Чтобы не ложился бот из-за ошибки и не записывал пустое в БД.
        if booking == {"type": None, "category": None, "contact": None, "addr": []}:
            return 666
        filename = "datebase.json"
        with open(filename, "r", encoding="UTF-8") as datebase:
            data = json.loads(datebase.read())
            if data[booking["date"]][call.data[5:]]:
                bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                          text='Это время уже занято, выберите другое')
            else:
                booking['time'] = []

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
                booking['time'].append(call.data[5:])
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
                    booking['time'].append(next_half_hour)

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
                        booking['time'].append(prev_half_hour)
                    next_half_hour = this_hour + ":30" if this_minutes == "00" else str(int(this_hour) + 1) + ":00"
                    # Проверка, не является ли выбранная дата верхней границей по времени
                    if next_half_hour != str(config.day_border[1][0]) + ":" + str(config.day_border[1][1]) \
                            and this_hour + ":" + this_minutes != str(config.day_border[1][0]) + ":" + str(
                        config.day_border[1][1]):
                        # Проверка, занят ли последующий получасовой интервал
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
                        booking['time'].append(next_half_hour)

                write_database(data, filename)

                # Сделать подтверждение ->
                inline_keyboard = telebot.types.InlineKeyboardMarkup()
                inline_keyboard.row(types.InlineKeyboardButton("Изменить дату", callback_data="warning_change_date"),
                                    types.InlineKeyboardButton("Отменить запись", callback_data="warning_cancel"))

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item = types.KeyboardButton("Записаться")
                markup.add(item)

                type_category_msg = booking['type'].capitalize() + " " + booking['category'] if \
                    booking['category'].lower() != "тейпирование" else "Тейпирование"
                s_msg = 'Пользователь ' + call.from_user.first_name + ' записался на\n-> "' \
                        + type_category_msg + '",\n-> ' + booking['date'] \
                        + '\n-> Время: ' + call.data[5:] + '\n-> Instagram: ' + booking['contact']
                # addr_msg = '\n-> Адрес: ' + booking['addr'] if booking['addr'] is not None else ""
                if booking['addr']:
                    if booking['addr'][0] == 'addr':
                        s_msg += '\n-> Адрес: ' + booking['addr'][1]
                        bot.send_message(admin_id, s_msg)
                    elif booking['addr'][0] == 'location':
                        bot.send_message(admin_id, s_msg)
                        bot.send_location(admin_id, booking['addr'][1], booking['addr'][2])
                else:
                    bot.send_message(admin_id, s_msg)

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


def delete_record(filename, call):
    global booking
    with open(filename, "r", encoding="UTF-8") as datebase:
        data = json.loads(datebase.read())
        try:
            for time_taken in booking['time']:
                data[booking['date']][time_taken] = []
            write_database(data, filename)
            type_category_msg = booking['type'].capitalize() + " " + booking['category'] if \
                booking['category'].lower() != "тейпирование" else "Тейпирование"
            s_msg = 'Пользователь ' + call.from_user.first_name + ' отменил свою запись на\n-> "' \
                    + type_category_msg + '",\n-> ' + booking['date'] \
                    + '\n-> Instagram: ' + booking['contact']
            if booking['addr']:
                if booking['addr'][0] == 'addr':
                    s_msg += '\n-> Адрес: ' + booking['addr'][1]
                    bot.send_message(admin_id, s_msg)
                elif booking['addr'][0] == 'location':
                    bot.send_message(admin_id, s_msg)
                    bot.send_location(admin_id, booking['addr'][1], booking['addr'][2])
            else:
                bot.send_message(admin_id, s_msg)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton("Записаться")
            markup.add(item)
            bot.send_message(call.message.chat.id, "Ваша запись успешно отменена.", reply_markup=markup)
        except KeyError:
            records = []
            for date in data:
                for timeshift in data[date]:
                    if data[date][timeshift]:
                        if "is_start_time" in data[date][timeshift][1]:
                            if data[date][timeshift][0] == call.message.chat.id:
                                records.append([date, timeshift, data[date][timeshift][1]])
            if records is None:
                bot.answer_callback_query(call.id, "Ничего не найдено. Вы ни на что не записаны", show_alert=True)
            else:
                s_msg = ""
                for record in records:
                    type_category_msg = record[2]['type'].capitalize() + " " + record[2]['category'] if \
                        record[2]['category'].lower() != "тейпирование" else "Тейпирование"
                    s_msg += "--> " + record[0] + " " + record[1] + "\n" + type_category_msg + "\n\n"
                bot.send_message(call.message.chat.id, s_msg)
                sent = bot.send_message(call.message.chat.id,
                                        "Выберите запись, которую Вы собираетесь отменить. Скопируйте и отправьте мне дату из сообщения, так как там, число с точками после стрелочки вначале.\nВнимание! Это удалит все записи на выбранный день, если у Вас их несколько.")
                bot.register_next_step_handler(sent, delete_chosen_record)


def delete_chosen_record(message):
    filename = "datebase.json"
    records_deleted = []
    try:
        # date, timeshift = message.text.split(" ")
        date = message.text.strip()
        with open(filename, "r", encoding="UTF-8") as datebase:
            data = json.loads(datebase.read())
            for time_taken in data[date]:
                if data[date][time_taken]:
                    if data[date][time_taken][0] == message.chat.id:
                        if "is_start_time" in data[date][time_taken][1]:
                            records_deleted.append(date + " " + time_taken)
                        data[date][time_taken] = []
            write_database(data, filename)
            s_msg = "Пользователь " + message.from_user.first_name + " отменил все свои записи на " + date + " число.\nОтмененные записи:"
            for record in records_deleted:
                s_msg += "\n-> " + record
            bot.send_message(admin_id, s_msg)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton("Записаться")
            markup.add(item)
            bot.send_message(message.chat.id, "Ваша запись успешно отменена.", reply_markup=markup)
    except (ValueError, KeyError):
        bot.send_message(message.chat.id, "Ошибка. Неверный формат указанной даты")


# def black_list_handler(message, direction):
#     global past_black_user
#     if direction == 0:
#         with open("user_base.json", "r", encoding="UTF-8") as database:
#             data = json.loads(database.read())
#             try:
#                 search_param = int(message.text)
#             except ValueError:
#                 search_param = message.text
#                 place = search_param.find("@")
#                 search_param = search_param[place + 1:]
#             finally:
#                 i = 0
#                 for s_user in data['users']:
#                     if s_user['id'] == search_param or s_user['username'] == search_param:
#                         new_black_user = data['users'][i]
#                         del data['users'][i]
#                         data['items'] -= 1
#                         write_database(data, "user_base.json")
#                         with open("black_list.json", "r", encoding="UTF-8") as blackList:
#                             data = json.loads(blackList.read())
#                             black_id.append(new_black_user['id'])
#                             data['users'].append(new_black_user)
#                             all_data = {"items": data['items'] + 1, "users": data['users']}
#                             write_database(all_data, "black_list.json")
#                         bot.send_message(message.chat.id, "Сделано!", reply_markup=types.ReplyKeyboardRemove())
#                         return
#                     i += 1
#     if message.text == "Назад ➤":
#         admin(message)
#         return -1
#     else:
#         with open("black_list.json", "r", encoding="UTF-8") as database:
#             data = json.loads(database.read())
#             if direction == 5:
#                 data['items'] = data['items'] - 1
#                 try:
#                     obj_id = int(message.text)
#                 except ValueError:
#                     bot.send_message(message.chat.id, "Недопустимое значение идентификатора.",
#                                      reply_markup=types.ReplyKeyboardRemove())
#                     return 1
#                 i = 0
#                 for obj in data['users']:
#                     if obj['id'] == obj_id:
#                         past_black_user = data['users'][i]
#                         del data['users'][i]
#                         break
#                     i += 1
#                 write_database(data, "black_list.json")
#                 with open("user_base.json", "r", encoding="UTF-8") as white_list_base:
#                     data = json.loads(white_list_base.read())
#                     data['items'] = data['items'] + 1
#                     data['users'].append(past_black_user)
#                     write_database(data, "user_base.json")
#                 bot.send_message(message.chat.id, "Готово!", reply_markup=types.ReplyKeyboardRemove())
#                 return 0
#             for obj in data['users']:
#                 bot.send_message(message.chat.id, "id: " + str(obj['id']) + ". Имя: " + obj["first_name"],
#                                  reply_markup=types.ReplyKeyboardRemove())
#             if direction == 1:
#                 markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#                 item = types.KeyboardButton("Назад ➤")
#                 markup.add(item)
#                 sent = bot.send_message(message.chat.id, "Выберите пользователя, которого хотите удалить (id)",
#                                         reply_markup=markup)
#                 bot.register_next_step_handler(sent, black_list_handler, 5)
#             else:
#                 markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#                 for function in adm_functions:
#                     item = types.KeyboardButton(function)
#                     markup.add(item)
#                 item = types.KeyboardButton("Назад ➤")
#                 markup.add(item)
#                 sent = bot.send_message(message.chat.id, "Полный список доступных пользователей ↑",
#                                         reply_markup=markup)
#                 bot.register_next_step_handler(sent, admin_after)


def check_records(message):
    month = message.text[:2]
    if month[-1] == '.':
        month = month[0]
        year = message.text[2:]
    else:
        month = month
        year = message.text[3:]
    filename = "datebase.json"
    with open(filename, "r", encoding="UTF-8") as datebase:
        data = json.loads(datebase.read())
        message_s = ""
        sent_some = False
        cliche = {}
        if (config.day_border[0][1] == 0 and config.day_border[1][1] == 0) or (
                config.day_border[0][1] == 30 and config.day_border[1][1] == 30):
            amount = [config.day_border[1][0] - config.day_border[0][0], 0]
        elif config.day_border[0][1] == 0 and config.day_border[1][1] == 30:
            amount = [config.day_border[1][0] - config.day_border[0][0], 30]
        elif config.day_border[0][1] == 30 and config.day_border[1][1] == 0:
            amount = [config.day_border[1][0] - config.day_border[0][0] - 1, 30]
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
            cliche[new_hour + ":" + new_minutes] = []

        for date in data:
            if date[-2:] == year:
                dot_pos = date.find('.') + 1
                d_month = date[dot_pos:dot_pos + 2]
                d_month = d_month[0] if d_month[-1] == '.' else d_month
                if int(d_month) == int(month):
                    if data[date] != cliche:
                        for timeshift in data[date]:
                            if data[date][timeshift]:
                                if "is_start_time" in data[date][timeshift][1]:
                                    type_category_msg = data[date][timeshift][1]['type'].capitalize() + " " + \
                                                        data[date][timeshift][1]['category'] if \
                                        data[date][timeshift][1][
                                            'category'].lower() != "тейпирование" else "Тейпирование"

                                    message_s += '--> ' + date + '\nВремя: ' + timeshift + '\n' + type_category_msg + \
                                                 '\nКонтакт: ' + data[date][timeshift][1]['contact']

                                    if data[date][timeshift][1]['addr']:
                                        if data[date][timeshift][1]['addr'][0] == 'addr':
                                            message_s += '\nАдрес: ' + data[date][timeshift][1]['addr'][1] + '\n\n'
                                        elif data[date][timeshift][1]['addr'][0] == 'location':
                                            bot.send_message(message.chat.id, message_s)
                                            bot.send_location(message.chat.id, data[date][timeshift][1]['addr'][1],
                                                              data[date][timeshift][1]['addr'][2])
                                            message_s = ""
                                            sent_some = True
                                    else:
                                        message_s += '\n\n'

        if message_s == "" and sent_some is False:
            message_s = "Ничего не найдено.\nПроверьте правильность введенных данных и попробуйте снова"
        elif message_s == "":
            return 0
        bot.send_message(message.chat.id, message_s, reply_markup=types.ReplyKeyboardRemove())


def add_holiday(message):
    filename = "datebase.json"
    date = message.text.strip()
    available = True
    canceled = []
    with open(filename, "r", encoding="UTF-8") as datebase:
        data = json.loads(datebase.read())
        if date in data:
            for timeshift in data[date]:
                if data[date][timeshift]:
                    available = False
                    if data[date][timeshift][0] not in canceled:
                        canceled.append(data[date][timeshift][0])
            if available:
                data[date] = {"all-time": ["admin", {"category": "выходной"}]}
                write_database(data, filename)
                bot.send_message(admin_id, "Выходной на " + date + " успешно добавлен!")
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1 = types.KeyboardButton("Да")
                item2 = types.KeyboardButton("Нет")
                markup.add(item1, item2)
                sent = bot.send_message(admin_id, "На " + date +
                                        " уже есть некоторые записи. Хотите отменить их и все равно назначить выходной?",
                                        reply_markup=markup)
                bot.register_next_step_handler(sent, take_decision_holiday, [canceled, date, data])
        else:
            data[date] = {"all-time": ["admin", {"category": "выходной"}]}
            write_database(data, filename)
            bot.send_message(admin_id, "Выходной на " + date + " успешно добавлен!")


def take_decision_holiday(message, args):
    # args = [canceled, date]
    canceled = args[0]
    date = args[1]
    data = args[2]
    if message.text.lower() == "да":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("Записаться")
        markup.add(item)

        data[date] = {"all-time": ["admin", {"category": "выходной"}]}
        write_database(data, "datebase.json")
        bot.send_message(admin_id, "Выходной на " + date + "успешно добавлен!")

        for client in canceled:
            bot.send_message(client, "Ваша запись на " + date + " была отменена.\nПриносим извинения за неудобства.",
                             reply_markup=markup)
    elif message.text.lower() == "нет":
        bot.send_message(admin_id, "Принято.", reply_markup=types.ReplyKeyboardRemove())
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Да")
        item2 = types.KeyboardButton("Нет")
        markup.add(item1, item2)
        bot.send_message(admin_id, 'Неверный формат ответа. Отправьте сообщение, содержащее только "Да" или "Нет".')
        sent = bot.send_message(admin_id, "На " + date +
                                " уже есть некоторые записи. Хотите отменить их и все равно назначить выходной?",
                                reply_markup=markup)
        bot.register_next_step_handler(sent, take_decision_holiday, [canceled, date, data])


def mailing(message, arguments=None, user_id=None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Записаться")
    markup.add(item)
    with open("user_base.json", "r", encoding="UTF-8") as database:
        data = json.loads(database.read())
        if arguments:
            if user_id is not None:
                try:
                    sent = bot.send_message(user_id, message.text, reply_markup=markup)
                    bot.register_next_step_handler(sent, feedback, message.text)
                except ApiException:
                    bot.send_message(admin_id,
                                     "Вопрос не был отправлен, т.к. пользователь заблокировал бота или отправка сообщений ему невозможна.",
                                     reply_markup=markup)
                finally:
                    return 0
            for person in data:
                try:
                    if person != message.from_user.id:
                        sent = bot.send_message(person, message.text, reply_markup=markup)
                        bot.register_next_step_handler(sent, feedback, message.text)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    continue
                else:
                    continue
            return 0
        if message.content_type == 'text':
            for person in data:
                try:
                    if person != message.from_user.id:
                        bot.send_message(person, message.text, reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    continue
                else:
                    continue
            bot.send_message(message.chat.id, "Разослано.", reply_markup=markup)
        elif message.content_type == 'photo':
            raw = message.photo[2].file_id
            name = "mailing.jpg"
            file_info = bot.get_file(raw)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(name, "wb") as photo:
                photo.write(downloaded_file)
            for person in data:
                photo = open(name, "rb")
                try:
                    if person != message.from_user.id:
                        bot.send_photo(person, photo, reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    photo.close()
                    continue
                else:
                    photo.close()
                    continue
            bot.send_message(message.chat.id, "Разослано.", reply_markup=markup)
        elif message.content_type == 'document':
            raw = message.document.file_id
            name = "mailing" + message.document.file_name[-4:]
            file_info = bot.get_file(raw)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(name, "wb") as document:
                document.write(downloaded_file)
            for person in data:
                document = open(name, "rb")
                try:
                    if person != message.from_user.id:
                        bot.send_document(person, document, reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    document.close()
                    continue
                else:
                    document.close()
                    continue
            bot.send_message(message.chat.id, "Разослано.", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Неподдерживаемый тип файла", reply_markup=markup)


def q_user(message):
    try:
        user_id = int(message.text.strip())
    except ValueError:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton("/admin")
        markup.add(item)
        bot.send_message(admin_id,
                         "Ошибка: Неверный формат id.\nПроверьте правильность введенных данных и попробуйте снова.",
                         reply_markup=markup)
        return 1
    else:
        sent = bot.send_message(admin_id, "Какой вопрос Вы хотели бы задать?\n(Отправьте его следующим сообщением)")
        bot.register_next_step_handler(sent, mailing, arguments=True, user_id=user_id)


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
        if str(message.from_user.id) not in data:
            data[message.from_user.id] = {"first_name": message.from_user.first_name,
                                          "last_name": message.from_user.last_name,
                                          "username": message.from_user.username}
            write_database(data, filename)


bot.polling(none_stop=True)
