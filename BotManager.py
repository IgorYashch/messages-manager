import telebot
from telebot.types import BotCommand
from database import Database

TOKEN = "5234704497:AAE6oUCuL52vdQGa0SOU73r7otbtCAnWBdo"
FIRST_MANAGER_USERNAME = "egorchistov"

bot = telebot.TeleBot(TOKEN)

database = Database()

#-------------------------------------------------------------------------------
# Копим данные о том, кто есть кто
#-------------------------------------------------------------------------------

managers_ids = set([FIRST_MANAGER_USERNAME])
users_ids = dict()

def is_managers_message(message):
    print(message.from_user.username)
    print(managers_ids)
    return message.from_user.username in managers_ids

def add_to_managers(id):
    managers_ids.add(id)

def delete_from_managers(id):
    managers_ids.discard(id)



def is_users_message(message):
    return message.chat.id in users_ids

def add_to_users(id, topic_name):
    users_ids[id] = topic_name

def delete_from_users(id):
    del users_ids[id]

def get_users_topic_name(id):
    return users_ids[id]
    
#-------------------------------------------------------------------------------
# Начало работы
#-------------------------------------------------------------------------------

# Приветствие
@bot.message_handler(commands=['start'])
def get_started(message):
    if is_managers_message(message):
        command = [BotCommand(command='help', description='Помощь'),
                   BotCommand(command='create_topic', description='Создать тему'),
                   BotCommand(command='read_messages', description='Прочитать сообщение из темы'),
                   BotCommand(command='add_manager', description='Повысить до менеджера'),
                   BotCommand(command='exit', description='Выход')]
        bot.set_my_commands(command)

        msg = bot.reply_to(message, """\
Добрый день, мистер менеджер!
Вы можете узнать о доступных вам командах, написав /help
""")
    else:
        text = '''
Привет!
Это бот для управления сообщениями на различные темы.
Введите название темы:
'''
        msg = bot.send_message(message.chat.id, text)

        # messages = database.get_replies(message.chat.id)
        # if messages:
        #     bot.send_message(message.chat.id, "Вам сообщение из топика")
        #     for m in messages:
        #         bot.send_message(message.chat.id, m)

        bot.register_next_step_handler(message, get_topic_name)


# узнаем, менеджер этот пользователь или юзер
def get_topic_name(message):
    topic_name = message.text

    # Проверяем, что такой топик существует
    if database.is_topic(topic_name):
        add_to_users(message.chat.id, topic_name)

        msg = bot.reply_to(message, f"""\
Добро пожаловать в тему \"{topic_name}\"!
Все ваши сообщения будут записаны!
Вы всегда можете выйти из топика, используя команду /exit.
При этом вы получите ответ на свое сообщение,\
даже если будете находиться в другом топике.
""")

    else:
        bot.reply_to(message, "Тема не существует")



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
/exit
/add_manager
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
    
    # Проверка на существование темы и запись новой в БД
    if not database.is_topic(topic_name):
        database.create_topic(topic_name)
        text = f'Тема \"{topic_name}\" успешно создана.'
    else:
        text = f'Тема \"{topic_name}\" уже существует.'
    bot.send_message(message.chat.id, text)




# получение последних сообщений
@bot.message_handler(commands=['read_messages'], func=is_managers_message)
def read_messages(message):
    list_of_topics = database.get_list_of_topics()

    # (True, True) оптимизируют размер иконок и делают клавиатуру одноразовой
    user_markup = telebot.types.ReplyKeyboardMarkup(True, True)
    if len(list_of_topics) <= borders[1] - borders[0]:
        for topic in list_of_topics:
            user_markup.row(topic)
    else:
        small_list, left, right = small_list_of_topics(list_of_topics, borders)
        if left:
            user_markup.row('Предыдущие темы...')
        for topic in small_list:
            user_markup.row(topic)
        if right:
            user_markup.row('Следующие темы...')

    text = "Выберете тему:"
    msg = bot.send_message(message.chat.id, text, reply_markup=user_markup)
    bot.register_next_step_handler(msg, topic_selection_handler, read_topic_name_rm, read_messages)


def read_topic_name_rm(message):
    topic_name = message.text
    
    # Проверка на существование темы
    if not database.is_topic(topic_name):
        text = "Такой темы не существует"
        bot.send_message(message.chat.id, text)
        return

    for m in database.get_unread_messages(topic_name):
        bot.send_message(message.chat.id, m)


# надо это куда то завернуть по хорошему
borders = [0, 3]

def small_list_of_topics(list_of_topics, borders):
    if len(list_of_topics) - 1 < borders[1]:
        small_list = list_of_topics[borders[0]:]
        right = False
    else:
        small_list = list_of_topics[borders[0]:borders[1]]
        right = True
    left = True if borders[0] != 0 else False
    return small_list, left, right

# отправка сообщения конкретному пользователю
@bot.message_handler(commands=['write_to_user'], func=is_managers_message)
def write_to_user(message):

    list_of_topics = database.get_list_of_topics()

    # (True, True) оптимизируют размер иконок и делают клавиатуру одноразовой
    user_markup = telebot.types.ReplyKeyboardMarkup(True, True)
    if len(list_of_topics) <= borders[1] - borders[0]:
        for topic in list_of_topics:
            user_markup.row(topic)
    else:
        small_list, left, right = small_list_of_topics(list_of_topics, borders)
        if left:
            user_markup.row('Предыдущие темы...')
        for topic in small_list:
            user_markup.row(topic)
        if right:
            user_markup.row('Следующие темы...')

    text = f'Введите тему, про которую пойдет речь:'
    msg = bot.send_message(message.chat.id, text, reply_markup=user_markup)
    bot.register_next_step_handler(msg, topic_selection_handler, read_topic_name_wtu, write_to_user)
    # bot.handler_after_selection = read_topic_name_wtu
    # bot.handler_selection = write_to_user

def topic_selection_handler(message, handler_after_selection, handler_selection):
    if message.text == 'Предыдущие темы...':
        borders[0] -= len(borders)
        borders[1] -= len(borders)
        handler_selection(message)
    elif message.text == 'Следующие темы...':
        borders[0] += len(borders)
        borders[1] += len(borders)
        handler_selection(message)
    else:
        handler_after_selection(message)

def read_topic_name_wtu(message):
    topic_name = message.text

    # Проверка на существование темы
    if not database.is_topic(topic_name):
        text = "Такой темы не существует"
        bot.send_message(message.chat.id, text)
        return

    text = 'Введите id пользователя, которому хотите отправить сообщение:'
    # id пользователей должен выводиться при выводе списка сообщений
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, read_users_login_wtu, topic_name)

def read_users_login_wtu(message, topic_name):
    id = message.text
    
    # Проверка на существование пользователя
    if not database.has_user(id):
        text = "Этот пользователь не оставлял сообщений"
        bot.send_message(message.chat.id, text)
        return

    text = 'Введите сообщение:'
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
    if message.from_user.username == FIRST_MANAGER_USERNAME:
        text = 'Простите, но вы не можете уйти, вы главный менеджер'
    else:

        delete_from_managers(message.from_user.username)

        text = 'До свидания!\nДля начала новой сессии напишите /start'
    bot.send_message(message.chat.id, text)




# добавление нового месенжера
@bot.message_handler(commands=['add_manager'], func=is_managers_message)
def add_manager(message):
    text = 'Введите username нового менеджера'
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, read_manager_name)

def read_manager_name(message):
    add_to_managers(message.text)
    text = 'Новый менеджер добавлен!'
    msg = bot.send_message(message.chat.id, text)

#-------------------------------------------------------------------------------
# ОБРАБОТЧИКИ ДЛЯ ЮЗЕРА
#-------------------------------------------------------------------------------

# вывод справочной информации
@bot.message_handler(commands=['help'], func=is_users_message)
def send_help(message):
    text="""
Доступные команды:
/help
/exit
"""
    bot.send_message(message.chat.id, text)


# завершение сессии менеджера
@bot.message_handler(commands=['exit'], func=is_users_message)
def exit_session(message):
    delete_from_users(message.chat.id)

    text = 'До свидания!\nДля начала новой сессии напишите /start'
    bot.send_message(message.chat.id, text)


# отправка текстового сообщения
@bot.message_handler(content_types=['text'], func=is_users_message)
def read_message_and_save(message):
    msg_text = message.text
    id = message.chat.id

    # Запись этого сообщения в БД
    topic_name = get_users_topic_name(id)
    database.send_message(topic_name, id, msg_text)


#-------------------------------------------------------------------------------
# ОСТАВШИЕСЯ ВАРИАНТЫ ИСКЛЮЧЕНИЯ
#-------------------------------------------------------------------------------

@bot.message_handler(func=is_managers_message)
def reply_to(message):
    replied_message = message.reply_to_message

    if replied_message:
        user_id = database.get_user_id_for_message(replied_message.text)
        topic_name = database.get_topic_name_for_message(replied_message.text)

        bot.send_message(user_id, "Вам пришел новый ответ:")
        text = replied_message.text
        answer = message.text

        answer = f"""Тема: \"{topic_name}\"

Ваше сообщение: 
\"{text}\"

Ответ: 
\"{answer}\"
"""
        bot.send_message(user_id, answer)
    else:
        bad_message(message)

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
