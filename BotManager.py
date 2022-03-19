import telebot
import config

from database import get_conn, topics

bot = telebot.TeleBot(config.manager_token)

#database = None

#-------------------------------------------------------------------------------
# Копим данные о том, кто есть кто
#-------------------------------------------------------------------------------

managers_ids = set()
users_ids = set()

def is_managers_message(message):
    return message.chat.id in managers_ids

def is_users_message(message):
    return message.chat.id in users_ids

def add_to_managers(id):
    managers_ids.add(id)

def add_to_users(id):
    users_ids.add(id)

def delete_from_managers(id):
    managers_ids.discard(id)

def delete_from_users(id):
    users_ids.discard(id)
    
#-------------------------------------------------------------------------------
# Начало работы
#-------------------------------------------------------------------------------

# Приветствие
@bot.message_handler(commands=['start'])
def get_started(message):
    text = '''
Привет!
Это бот для управления сообщениями на различные темы.
Введи, пожалуйста секретный код темы
'''
    msg = bot.send_message(message.chat.id, text)

    bot.register_next_step_handler(message, get_secret_code)


# узнаем, менеджер этот пользователь или юзер
def get_secret_code(message):
    code = message.text

    if code == config.manager_code:
        add_to_managers(message.chat.id)

        msg = bot.reply_to(message, """\
Добрый день, мистер менеджер!
Вы можете узнать о доступных вам командах, написав /help
""")

    # Проверяем, что такой топик существует
    elif True: #database.is_topic_code(code):
        add_to_users(message.chat.id)

        msg = bot.reply_to(message, f"""\
Добро пожаловать в тему \"{"Имя топика"}\"!
Все ваши сообщения будут записаны!
Вы всегда можете выйти из топика, используя команду /exit.
При этом вы получите ответ на свое сообщение,\
даже если будете находиться в другом топике.
""")



#-------------------------------------------------------------------------------
# ОБРАБОТЧИКИ ДЛЯ МЕНЕДЖЕРА
#-------------------------------------------------------------------------------


# вывод справочной информации
@bot.message_handler(commands=['help'], func=is_managers_message)
def send_help(message):
    text="""
Доступные команды:
/help
/create_topic
/read_messages
/write_to_user
/exit
"""
    bot.send_message(message.chat.id, text)



# создание новой темы
@bot.message_handler(commands=['create_topic'], func=is_managers_message)
def create_topic(message):
    text = "Введите название темы:"
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, read_topic_name_ct)

def read_topic_name_ct(message):
    topic_name = message.text
    
    # YOUR CODE HERE
    # Проверка на существование темы и запись новой в БД

    text = f'Новая тема \"{topic_name}\" создана.\nСекретный пароль для нее:'
    msg = bot.send_message(message.chat.id, text)


    new_secret_code = 'Bla-bla-bla' # YOUR CODE HERE
    bot.send_message(message.chat.id, new_secret_code)




# получение последних сообщений
@bot.message_handler(commands=['read_messages'], func=is_managers_message)
def read_messages(message):
    text = "Введите название темы:"
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, read_topic_name_rm)

def read_topic_name_rm(message):
    topic_name = message.text
    
    # YOUR CODE HERE
    # Проверка на существование темы

    text = f'Сколько последних сообщений вы хотите увидеть?'
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, get_number_of_messages_rm)

def get_number_of_messages_rm(message):
    try:
        num = int(message.text)

        text = f"Здесь будет выведена информация о {num} сообщениях"
        bot.send_message(message.chat.id, text)

        # YOUR CODE HERE
        # Сбор информации из БД и их печать
    except:
        text = "Это не число. Ошибка выполнения команды."
        bot.send_message(message.chat.id, text)




# отправка сообщения конкретному пользователю
@bot.message_handler(commands=['write_to_user'], func=is_managers_message)
def write_to_user(message):
    text = f'Введите тему, про которую пойдет речь:'
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, read_topic_name_wtu)

def read_topic_name_wtu(message):
    topic_name = message.text
    
    # YOUR CODE HERE
    # Проверка на существование темы

    text = 'Введите id пользователя, которому хотите отправить сообщение:'
    # id пользователей должен выводиться при выводе списка сообщений
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, read_users_login_wtu, topic_name)

def read_users_login_wtu(message, topic_name):
    id = message.text
    
    # YOUR CODE HERE
    # Проверка на существование пользователя

    text = 'Введите само сообщение:'
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, read_message_wtu, topic_name, id)

def read_message_wtu(message, topic_name, id):
    message_text = message.text

    # YOUR CODE HERE
    # отправка сообщения конкретному юзеру 
    # (возможно красиво, с указанием темы и сообщения, на которое отвечают)
    # пользователь ведь может и закончить конкретную сессию на данный момент

    text = 'Ваш ответ направлен пользователю'
    bot.send_message(message.chat.id, text)



# завершение сессии менеджера
@bot.message_handler(commands=['exit'], func=is_managers_message)
def exit_session(message):
    delete_from_managers(message.chat.id)

    text = 'До свидания!\nДля начала новой сессии напишите /start'
    bot.send_message(message.chat.id, text)



#-------------------------------------------------------------------------------
# ОБРАБОТЧИКИ ДЛЯ ЮЗЕРА
#-------------------------------------------------------------------------------

# завершение сессии менеджера
@bot.message_handler(commands=['exit'], func=is_managers_message)
def exit_session(message):
    delete_from_managers(message.chat.id)

    text = 'До свидания!\nДля начала новой сессии напишите /start'
    bot.send_message(message.chat.id, text)


# отправка текстового сообщения
@bot.message_handler(content_types=['text'], func=is_users_message)
def read_message_and_save(message):
    msg_text = message.text
    id = message.chat.id

    # YOUR CODE HERE
    # Запись этого сообщения в БД

    text = 'Выше сообщение сохранено'
    bot.send_message(message.chat.id, text)


#-------------------------------------------------------------------------------
# ОСТАВШИЕСЯ ВАРИАНТЫ ИСКЛЮЧЕНИЯ
#-------------------------------------------------------------------------------

# Ошибка при запущенном режиме юзера/менеджера
@bot.message_handler(func=is_users_message)
@bot.message_handler(func=is_managers_message)
def bad_message(message):
    text = '''
Кажется, вы ошиблись...
Пожалуйста, ведите команду /help, чтобы ознакомиться с командами
'''
    msg = bot.send_message(message.chat.id, text)


# Спам в момент между сессиями
@bot.message_handler(func=lambda x: True)
def bad_message(message):
    text = '''
Кажется, вы ошиблись...
Пожалуйста, ведите команду /start
'''
    msg = bot.send_message(message.chat.id, text)



#-------------------------------------------------------------------------------
# ГЛАВНЫЙ ЦИКЛ
#-------------------------------------------------------------------------------


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
