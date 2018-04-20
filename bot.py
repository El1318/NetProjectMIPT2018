import config
import telebot
from telebot import apihelper

bot = telebot.TeleBot(config.token)
proxy = config.proxy()
apihelper.proxy = {'https':'socks5://'+proxy.user+":"+proxy.password+"@"+proxy.address+":"+proxy.port}

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): # Название функции не играет никакой роли, в принципе
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    bot.polling(none_stop=True)