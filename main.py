import telebot
from telebot.apihelper import ApiException

import config
import json
import time
from datetime import datetime
from telebot import types

bot = telebot.TeleBot(config.TOKEN)
# time.altzone = -10800  Смещение на часовой пояс GMT +3

# adm_functions = ['Вакансии', 'Черный список', 'Установить частоту оповещений', 'Рассылка', 'Провести опрос']
adm_functions = ['Вакансии', 'Черный список', 'Просмотреть Базу Данных', 'Отправить сообщение-вопрос', 'Рассылка']
vacancy_functions = ["Добавить вакансию", "Удалить вакансию", "Просмотреть текущий список вакансий"]
black_list_functions = ['Добавить пользователя в черный список', 'Удалить пользователя из черного списка',
                        'Просмотреть черный список']
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
        bot.send_message(message.chat.id, "У Вас недостаточно прав для использования этой функции.", reply_markup=markup)


def admin_after(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item = types.KeyboardButton("Записаться")
    markup.add(item)
    if message.from_user.id == admin_id:
        if message.text == "Рассылка":
            sent = bot.send_message(message.chat.id, "Какое сообщение Вы хотите разослать?",
                                    reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(sent, mailing)
        elif message.text == 'Черный список':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for function in black_list_functions:
                item = types.KeyboardButton(function)
                markup.add(item)
            sent = bot.send_message(message.chat.id, "Что бы Вы хотели сделать?", reply_markup=markup)
            bot.register_next_step_handler(sent, admin_after)
        elif message.text == black_list_functions[0]:
            sent = bot.send_message(message.chat.id,
                                    "Введите данные пользователя, которого Вы хотите добавить в черный список: ",
                                    reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(sent, black_list_handler, 0)
        elif message.text == black_list_functions[1]:
            black_list_handler(message, 1)
        elif message.text == black_list_functions[2]:
            black_list_handler(message, 2)
        elif message.text == 'Просмотреть Базу Данных':
            show_database()
        elif message.text == 'Отправить сообщение-вопрос':
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
        elif message.text == 'Выбрать пользователя':
            new_message = ""
            with open("user_base.json", "r", encoding="UTF-8") as database:
                data = json.loads(database.read())
                for s_user in data:
                    new_message += "Имя: " + s_user['first_name'] + ", id: " + str(s_user) + ";\n"
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


@bot.message_handler(content_types=['text'], commands=['start'], func=lambda message: message.chat.id not in black_id)
def chat(message):
    initialisation(message)
    if message.chat.type == 'private':
        if message.text.lower() == 'привет' or message.text.lower() == 'записаться' or message.text == '/start':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Очная")
            item2 = types.KeyboardButton("Заочная")
            markup.add(item1, item2)
            booking = {}
            sent = bot.send_message(message.chat.id,
                                    "Здравствуй, <b>{0.first_name}</b>!\nЯ бот, который поможет Вам забронировать консультацию.\nВы хотели бы выбрать очную или заочную консультацию?".format(
                                        message.from_user), parse_mode='html', reply_markup=markup)
            bot.register_next_step_handler(sent, choose_type, booking)


def choose_type(message, booking):
    if message.text.lower() == "очная" or message.text.lower() == "заочная":
        red_border = {"y": time.strftime("%Y"),
                      "m": [time.strftime("%m"), time.strftime("%B")],
                      "d": [time.strftime("%d"), time.strftime("%a")]}
        name_line = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
        # week_name_line = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        second_line = []
        days_array_0, days_array_1, days_array_2, days_array_3, days_array_4, days_array_5 = [], [], [], [], [], []
        first_day = datetime(int(red_border['y']), int(red_border['m'][0]), 1).weekday()
        print(first_day)
        if first_day != 0:
            for i in range(6):
                if i+1 != first_day:
                    days_array_0.append(types.InlineKeyboardButton("x", callback_data="0"))
                else:
                    break
        for day_name in name_line:
            second_line.append(types.InlineKeyboardButton(day_name, callback_data="0"))
        for day in range(31):
            value = "0" if day + 1 <= int(red_border["d"][0]) else str(day + 1) + "." + red_border["m"][0]
            new_button = types.InlineKeyboardButton(str(day+1), callback_data=str(value))
            if len(days_array_0) < 7:
                days_array_0.append(new_button)
            elif len(days_array_1) < 14:
                days_array_1.append(new_button)
            elif len(days_array_2) < 21:
                days_array_2.append(new_button)
            elif len(days_array_3) < 28:
                days_array_3.append(new_button)
            elif len(days_array_3) < 35:
                days_array_4.append(new_button)
            else:
                days_array_5.append(new_button)
        i = 1
        new_month = str(int(red_border['m'][0]) + 1)
        if len(days_array_5) != 0:
            while len(days_array_5) < 7:
                days_array_5.append(types.InlineKeyboardButton(str(i), callback_data=str(i)+"."+new_month))
                i += 1
        inline_keyboard = types.InlineKeyboardMarkup([[types.InlineKeyboardButton("<", callback_data="m_back"),
                                                       types.InlineKeyboardButton(red_border["m"][1], callback_data="0"),
                                                       types.InlineKeyboardButton(">", callback_data="m_next")],
                                                      second_line,
                                                      days_array_0, days_array_1, days_array_2,
                                                      days_array_3, days_array_4, days_array_5],
                                                     row_width=7)

        booking['type'] = message.text
        bot.send_message(message.chat.id, "Принято.")
        sent = bot.send_message(message.chat.id, "Выберите дату консультации >", reply_markup=inline_keyboard)
        bot.register_next_step_handler(sent, choose_date, booking)
    else:
        sent = bot.send_message(message.chat.id, 'Некорректный формат введенных данных, отправьте сообщение с одним словом "Очная" либо "Заочная"')
        bot.register_next_step_handler(sent, choose_type, booking)


def choose_date(message, booking):
    # Допустим, что дата подается в верном формате, например, через callback-query selector
    booking['date'] = message.text
    bot.send_message(message.chat.id, "Принято.")
    sent = bot.send_message(message.chat.id, "Выберите время консультации")
    bot.register_next_step_handler(sent, choose_time, booking)


def choose_time(message, booking):
    # Допустим, что время подается в верном формате, например, через callback-query selector
    booking['time'] = message.text
    bot.send_message(message.chat.id, "Принято.")
    if booking['type'] == "Очная":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton(text="Отправить мое местоположение", request_location=True)
        markup.add(item)
        sent = bot.send_message(message.chat.id, "Укажите Ваш адрес, где будет проходить консультации")
        bot.register_next_step_handler(sent, choose_addr, booking)
    else:
        booking['addr'] = None


def choose_addr(message, booking):
    booking['addr'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Да, отправить")
    item2 = types.KeyboardButton("Нет")
    markup.add(item1, item2)
    message = "Тип консультации: " + booking['type'] + "\nДата консультации: " + booking['date'] + \
              "\nВремя консультации: " + booking['time'] + "\nАдрес: " + booking['addr']
    bot.send_message(message.chat.id, message)
    sent = bot.send_message(message.chat.id, "Готово.\n\n" + message + "\n\nОтправить заявку?", reply_markup=markup)
    bot.register_next_step_handler(sent, confirm, booking)


def confirm(message, booking):
    if message.text == "Да, отправить" or message.text.lower() == "да":
        pass
    else:
        pass


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


def mailing(message, arguments=None, user_id=None):
    markup = back_markup()
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
            for person in data['users']:
                try:
                    if person['id'] != message.from_user.id:
                        sent = bot.send_message(person['id'], message.text, reply_markup=markup)
                        bot.register_next_step_handler(sent, feedback, message.text)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    continue
                else:
                    continue
            return 0
        if message.content_type == 'text':
            for person in data['users']:
                try:
                    if person['id'] != message.from_user.id:
                        bot.send_message(person['id'], message.text, reply_markup=markup)
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
            for person in data['users']:
                photo = open(name, "rb")
                try:
                    if person['id'] != message.from_user.id:
                        bot.send_photo(person['id'], photo, reply_markup=markup)
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
            for person in data['users']:
                document = open(name, "rb")
                try:
                    if person['id'] != message.from_user.id:
                        bot.send_document(person['id'], document, reply_markup=markup)
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
            # Фильтр от ботов. По идее, бот боту написать сообщение не может, но пусть будет
            if message.from_user.is_bot:
                bot.send_message(message.chat.id, "Я с ботами не общаюсь : )", reply_markup=types.ReplyKeyboardRemove())
                with open("black_list.json", "r", encoding="UTF-8") as black_list:
                    data = json.loads(black_list.read())
                    filename = "black_list.json"
                    black_id.append(message.from_user.id)
            data[message.from_user.id] = {"first_name": message.from_user.first_name,
                                          "last_name": message.from_user.last_name,
                                          "username": message.from_user.username}
            write_database(data, filename)


bot.polling(none_stop=True)
