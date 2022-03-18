# Предупреждаю, что все текстовые сообщения написаны от балды

import telebot
import config

#import subbot


bot = telebot.TeleBot(config.manager_token)


database = None


@bot.message_handler(commands=['start'])
def get_started(message):
	text = 'Привет!\n Это бот для управления сообщения на различные темы.'
	bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['help'])
def get_started(message):
	# Потом мб изменим интерфейс и способ ввода, потому что последние 2 команды так не реализовать
	text = """Памятка по командам:
	/start - запуск бота
	/help - вывод информации по командам
	/create_topic - создание нового бота для конкретной темы
	/get_messages - получение сообщений из бд
	/sent_answer - отправка ответа на одно из сообщений пользователя
	"""
	bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['create_topic'])
def create_topic(message):
	# Создаем здесь новый процесс и запускаем в нем новый бот
	# Узнаем у него ник и отправляем человеку-менеджеру или сразу в какой-нибудь канал (надо тоже решить)
	# Я плохо знаком с параллельными процессами в питоне, так что хз где заставить его отправлять сообщения сюда.
	# Мб просто дать доступ sub ботам к БД и сделать на ней блокировку и не париться об этом

	text = 'Новый топик создан (надо придумать, как передавать имя топика)'
	bot.send_message(message.chat.id, text)




if __name__ == '__main__':
	bot.polling(none_stop=True, interval=0)