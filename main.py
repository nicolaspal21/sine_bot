import telebot
from telebot import types
import sqlite3
import quandl
import matplotlib.pyplot as plt
import math as m

import COVID19Py

import requests
import datetime

TOKEN = "2035055117:AAEeeH2R8p3bXdPjAtdtRUMZt2iDxRIBWEk"

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
# подключим токен нашего бота
bot = telebot.TeleBot(TOKEN)

covid19 = COVID19Py.COVID19()
latest = covid19.getLatest()

# напишем, что делать нашему боту при команде старт
@bot.message_handler(commands=['start'])
def send_keyboard(message, text="Привет, чем я могу тебе помочь?"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)  # наша клавиатура

    itembtn1 = types.KeyboardButton('Погода в Москве')
    itembtn2 = types.KeyboardButton('Фонд Рынок')

    itembtn11 = types.KeyboardButton('Пока все!')

    keyboard.add(itembtn1, itembtn2) # Мои

    keyboard.add(itembtn11)
    # но если кнопок слишком много, они пойдут на след ряд автоматически

    # пришлем это все сообщением и запишем выбранный вариант
    msg = bot.send_message(message.from_user.id,
                     text=text, reply_markup=keyboard)

    # отправим этот вариант в функцию, которая его обработает
    bot.register_next_step_handler(msg, callback_worker)

def callback_worker(call):
    final_message = ''

    if call.text == "Погода в Москве":
        msg_3 = bot.send_message(call.chat.id, 'Нажмите кнопку еще раз!')
        bot.register_next_step_handler(msg_3, callback_worker_3)

    elif call.text == "Фонд Рынок":
        keyboard = types.ReplyKeyboardMarkup(row_width=2)  # наша клавиатура
        itembtn1 = types.KeyboardButton('Нефть')  # создадим кнопку
        itembtn2 = types.KeyboardButton('EURUSD')

        keyboard.add(itembtn1,itembtn2)  # добавим кнопки 1 и 2 на первый ряд
        #keyboard.add(itembtn3, itembtn4, itembtn5, itembtn6)  # добавим кнопки 3, 4, 5 на второй ряд
        # пришлем это все сообщением и запишем выбранный вариант
        msg_4 = bot.send_message(call.chat.id,
                               text=call.text, reply_markup=keyboard)
        # отправим этот вариант в функцию, которая его обработает
        bot.register_next_step_handler(msg_4, callback_worker_4)

    elif call.text == "Пока все!":
        bot.send_message(call.chat.id, 'Хорошего дня! Когда захотите продолжнить нажмите на команду /start')


@bot.message_handler(content_types=['text'])
def handle_docs_audio(message):
    send_keyboard(message, text="Я не понимаю :-( Выберите один из пунктов меню:")

"""
Мои функций (Николай)
"""

def get_weather(call):
    """
    Програмка прогноза погоды в москве с сайта  openweathermap
    """
    city = "moscow"
    open_weather_token = '79505156a402ffd36412de72f4cbce46'
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

    bot.send_message(call.chat.id, f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
                                   f"Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n"
                                   f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
                                   f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n"
                                   f"***Хорошего дня!***"
                     )

# функция импорта графика с quandl
def grafik(call):
    import_name = {
        "Нефть": "FRED/DCOILBRENTEU",
        "EURUSD": "ECB/EURUSD"
    }
    quandl.ApiConfig.api_key = "Apnzsot_QRPgvhw6WyMb"
    data = quandl.get(import_name[call.text], start_date="2021-01-01")
    a = data.index
    b = data['Value']
    plt.plot(a, b)
    plt.savefig(call.text + '.png')
    plt.clf() # удаляет график для повторного использования
    bot.send_photo(call.chat.id, photo=open(call.text + '.png', 'rb'))

"""
Окончание блока функций моих (Николай)

Мои Callback (Николай)
"""

# привязываем функции к кнопкам на клавиатуре
def callback_worker_3(call):
    get_weather(call)
    send_keyboard(call, "Чем еще могу помочь?")

def callback_worker_4(call):

    grafik(call)
    send_keyboard(call, "Чем еще могу помочь?")

bot.polling(none_stop=True)