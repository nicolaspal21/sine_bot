import telebot
from telebot import types
import sqlite3
import quandl
import matplotlib.pyplot as plt
import math as m

import constants

import requests
import datetime

# реализация через файлик
#with open("token", "r") as f:
#    TOKEN = f.read

# через переменные окружения
import os
TOKEN = os.getenv("token_bot")

# новая реализация, обернем в класс
# на самом деле б/д нигде не использовалась, в процессе панического написания кода перед деделайном просто забыли удалить

class DataBase:
    def init_db():
        # подключаем базу данных
        conn = sqlite3.connect('planner_hse.db')

        # курсор для работы с таблицами
        cursor = conn.cursor()

        try:
            # sql запрос для создания таблицы
            query = "CREATE TABLE \"planner\" (\"ID\" INTEGER UNIQUE, \"user_id\" INTEGER, \"plan\" TEXT, PRIMARY KEY (\"ID\"))"
            # исполняем его –> ура, теперь у нас есть таблица, куда будем все сохранять!
            cursor.execute(query)
        except:
            pass

# вызовем метод для создания б/д
DataBase.init_db()

# подключим токен нашего бота
bot = telebot.TeleBot(TOKEN)


if __name__ == '__main__':

    # напишем, что делать нашему боту при команде старт
    @bot.message_handler(commands=['start'])
    def send_keyboard(message, text=constants.hello):
        keyboard = types.ReplyKeyboardMarkup(row_width=constants.width_row)  # наша клавиатура

        itembtn_weather_in_moscow = types.KeyboardButton(constants.weather_in_moscow)
        itembtn_fond_market = types.KeyboardButton(constants.fond_market)

        itembtn_fin = types.KeyboardButton(constants.fin)

        keyboard.add(itembtn_weather_in_moscow, itembtn_fond_market)
        keyboard.add(itembtn_fin)

        # пришлем это все сообщением и запишем выбранный вариант
        msg = bot.send_message(message.from_user.id,
                         text=text, reply_markup=keyboard)

        # отправим этот вариант в функцию, которая его обработает
        bot.register_next_step_handler(msg, callback_worker)


    def callback_worker(call):
        final_message = ''

        if call.text == constants.weather_in_moscow:
            msg_3 = bot.send_message(call.chat.id, constants.click_again)
            bot.register_next_step_handler(msg_3, callback_worker_weather)

        elif call.text == constants.fond_market:
            keyboard = types.ReplyKeyboardMarkup(row_width=constants.width_row)  # наша клавиатура
            itembtn_oil = types.KeyboardButton(constants.oil)  # создадим кнопку
            itembtn_eur_usd = types.KeyboardButton(constants.eur_usd)

            keyboard.add(itembtn_oil,itembtn_eur_usd)  # добавим кнопки на первый ряд

            # пришлем это все сообщением и запишем выбранный вариант
            msg_4 = bot.send_message(call.chat.id,
                                   text=call.text, reply_markup=keyboard)
            # отправим этот вариант в функцию, которая его обработает
            bot.register_next_step_handler(msg_4, callback_worker_chart)

        elif call.text == constants.fin:
            bot.send_message(call.chat.id, constants.good_day)


    @bot.message_handler(content_types=['text'])
    def handle_docs_audio(message):
        send_keyboard(message, text=constants.dont_understand)


    def get_weather(call):
        """
        Програмка прогноза погоды в москве с сайта  openweathermap
        """
        city = "moscow"
        open_weather_token = os.getenv("token_weather")
        code_to_smile = {
            "Clear": "Ясно \U00002600",
            "Clouds": "Облачно \U00002601",
            "Rain": "Дождь \U00002614",
            "Drizzle": "Дождь \U00002614",
            "Thunderstorm": "Гроза \U000026A1",
            "Snow": "Снег \U0001F328",
            "Mist": "Туман \U0001F32B"
        }
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={open_weather_token}&units=metric"
        )
        data = r.json()
        city = data["name"]
        cur_weather = data["main"]["temp"]
        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Посмотри в окно, не пойму что там за погода!"

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])


        def weather_info():

            return f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n" \
                                       f"Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n" \
                                       f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n" \
                                       f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\n" \
                                       f"Продолжительность дня: {length_of_the_day}\n" \
                                       f"***Хорошего дня!***"

        bot.send_message(call.chat.id, weather_info())

    # функция импорта графика с quandl
    def import_chart(call):
        import_name = {
            "Нефть": "FRED/DCOILBRENTEU",
            "EURUSD": "ECB/EURUSD"
        }

        def get_data_quandl():
            '''
            получение данных из quandl
            '''
            quandl.ApiConfig.api_key = os.getenv("token_quandl")
            data = quandl.get(import_name[call.text], start_date=constants.date_for_chart)

            return data

        def get_chart(data):
            '''
            построение и сохранение графика
            '''
            a = data.index
            b = data['Value']
            plt.plot(a, b)
            plt.savefig(call.text + '.png')
            plt.clf() # удаляет график для повторного использования

        data_q = get_data_quandl() # получим данные

        get_chart(data_q) # построим график

        # отправим график в виде сообщения
        bot.send_photo(call.chat.id, photo=open(call.text + '.png', 'rb'))

    # привязываем функции к кнопкам на клавиатуре
    def callback_worker_weather(call):
        get_weather(call)
        send_keyboard(call, constants.help)

    def callback_worker_chart(call):
        import_chart(call)
        send_keyboard(call, constants.help)

    bot.polling(none_stop=True)
