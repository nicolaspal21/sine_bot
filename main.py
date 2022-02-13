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

    # Евгений
    itembtn3 = types.KeyboardButton('разы в дБ')  # создадим кнопку
    itembtn4 = types.KeyboardButton('дБ в разы')
    itembtn5 = types.KeyboardButton('дБ в КСВН')
    itembtn6 = types.KeyboardButton("Построить график S параметров")

    # Даниял
    itembtn7 = types.KeyboardButton('Россия')  # создадим кнопку
    itembtn8 = types.KeyboardButton('США')
    itembtn9 = types.KeyboardButton('Норвегия')
    itembtn10 = types.KeyboardButton("Украина")

    itembtn11 = types.KeyboardButton('Пока все!')

    keyboard.add(itembtn1, itembtn2) # Мои
    keyboard.add(itembtn3, itembtn4, itembtn5, itembtn6) # Евгений
    keyboard.add(itembtn7, itembtn8) # Даниял
    keyboard.add(itembtn9, itembtn10)
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

    elif (call.text == "разы в дБ") or (call.text == "дБ в разы") or (call.text == "дБ в КСВН") or (call.text == "Построить график S параметров"):
        msg_5 = bot.send_message(call.chat.id, 'Нажмите кнопку еще раз!')
        bot.register_next_step_handler(msg_5, callback_worker_evg)

    elif call.text == "Россия":
        location = covid19.getLocationByCountryCode("RU")
        final_message = f"Заболевших: {location[0]['latest']['confirmed']:,}"
        bot.send_message(call.chat.id, final_message)
    elif call.text == "США":
        location = covid19.getLocationByCountryCode("US")
        final_message = f"Заболевших: {location[0]['latest']['confirmed']:,}"
        bot.send_message(call.chat.id, final_message)
    elif call.text == "Украина":
        location = covid19.getLocationByCountryCode("UA")
        final_message = f"Заболевших: {location[0]['latest']['confirmed']:,}"
        bot.send_message(call.chat.id, final_message)
    elif call.text == "Норвегия":
        location = covid19.getLocationByCountryCode("NO")
        final_message = f"Заболевших: {location[0]['latest']['confirmed']:,}"
        bot.send_message(call.chat.id, final_message)


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
Начало блока функций от Евгения
"""

# вызываемые функции
def times_to_dB(dB): # функция перевода разов в дБ
    if dB.text.isdigit():
        num_dB = float(dB.text)
        result = 10 * m.log(num_dB, 10)
        bot.send_message(dB.chat.id, str("%.4f" % result) + ' дБ')
    else:
        bot.send_message(dB.chat.id, "Вы ввели не число или число меньше нуля")
    send_keyboard(dB, "Чем еще могу помочь?")

def dB_to_times(times): # функция перевода дБ в разы
    specialChars = ",.-"
    txt = times.text
    for specialChar in specialChars:
        txt = txt.replace(specialChar, '')

    if txt.isdigit():
        num_times = float(times.text)
        result = 10 ** (num_times / 10)
        bot.send_message(times.chat.id, str("%.4f" % result))
    else:
        bot.send_message(times.chat.id, "Вы ввели не число")
    send_keyboard(times, "Чем могу быть полезен?")

def dB_to_VSWR(VSWR): # функция вычисляющая КСВН
    specialChars = ",.-"
    txt = VSWR.text
    for specialChar in specialChars:
        txt = txt.replace(specialChar, '')

    if txt.isdigit() and float(VSWR.text) < 0.0:
        num = 10 ** (float(VSWR.text) / 20)
        result = (1 + abs(num)) / (1 - abs(num))
        bot.send_message(VSWR.chat.id, str("%.4f" % result))
    else:
        bot.send_message(VSWR.chat.id, "Вы ввели не число или число больше нуля")
    send_keyboard(VSWR, "Чем могу быть полезен?")

def plot_sparams(data_list, y_min, y_max, S_param_name): # рисуем график S параметра
    x = []
    y = []
    for i in range(len(data_list)):
        x.append(data_list[i][0])
        y.append(data_list[i][1])

    plt.plot(x, y);
    plt.ylim([y_min, y_max])
    plt.grid('true')
    plt.xlabel('Частота, ГГц')
    plt.ylabel(S_param_name + ' дБ')
    plt.title('Грифк зависимости ' + S_param_name + ' от частоты')
    fig_name = S_param_name
    plt.savefig(fig_name)
    return fig_name

def prints(doc_data):
    if doc_data.content_type != 'document':
        bot.send_message(doc_data.chat.id, "Ошибка чтения файла")
        send_keyboard(doc_data, "Чем могу быть полезен?")

    file_object = bot.get_file(doc_data.document.file_id)
    #print(doc_data)
    path = file_object.file_path
    path_to_file = "https://api.telegram.org/file/bot" + TOKEN + "/" + path
    response = requests.get(path_to_file)
    data_file = response.text
    data_file = data_file.replace('\r', '')
    data_str = data_file.split('\n')
    data_list = []
    for x in data_str:
        data_list.append(list(map(float, x.split(' '))))

    try:
        S_param_name = '' + doc_data.caption

    except:
        S_param_name = 'clear'
    plot_name = plot_sparams(data_list, -30, 0, S_param_name)
    bot.send_photo(doc_data.chat.id, photo=open(plot_name + '.png', 'rb'))
    send_keyboard(doc_data, "Чем еще могу помочь?")

"""
Окончание блока функций от Евгения
Мои Callback (Николай)
"""

# привязываем функции к кнопкам на клавиатуре
def callback_worker_3(call):
    get_weather(call)
    send_keyboard(call, "Чем еще могу помочь?")

def callback_worker_4(call):

    grafik(call)
    send_keyboard(call, "Чем еще могу помочь?")

"""
Callback Евгения
"""

def callback_worker_evg(call):
    if call.text == "разы в дБ":
        msg_times = bot.send_message(call.chat.id, 'Прошу ввести величину в разах (больше нуля)')
        bot.register_next_step_handler(msg_times, times_to_dB)

    elif call.text == "дБ в разы":
        msg_dB = bot.send_message(call.chat.id, 'Прошу ввести величину в дБ')
        bot.register_next_step_handler(msg_dB, dB_to_times)

    elif call.text == "дБ в КСВН":
        msg_VSWR = bot.send_message(call.chat.id, 'Прошу ввести величину в дБ')
        bot.register_next_step_handler(msg_VSWR, dB_to_VSWR)

    elif call.text == "Построить график S параметров":
        doc_data = bot.send_message(call.chat.id, 'Прошу данные для графика')
        bot.register_next_step_handler(doc_data, prints)

    elif call.text == "Другое":
        bot.send_message(call.chat.id, 'Неверный запрос')
        send_keyboard(call, "Можете повторить команду?")

    #send_keyboard(call, "Чем еще могу помочь?")

""" 
Окончание Callback Евгения
"""


bot.polling(none_stop=True)