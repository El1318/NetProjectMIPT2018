import config
import artm_model
import db
import telebot
from telebot import apihelper

bot = telebot.TeleBot(config.token)
if config.proxy == True:
    proxy = config.proxy_settings()
    apihelper.proxy = {'https':'socks5://'+proxy.user+":"+proxy.password+"@"+proxy.address+":"+proxy.port}

model = artm_model.model
theta = artm_model.theta

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    doc_file = open("message.txt", "w")
    doc_file.write(message.text)
    doc_file.close()
    response = artm_model.transform(model, "message.txt", 'filename')
    doc_ids = artm_model.get_docs_ids_by_topic(theta, response[0])
    response = db.collection.find_one({'_id': config.id_prefix+str(doc_ids[0])}, projection = ['title', 'url'])
    bot.send_message(message.chat.id, str(response))


if __name__ == '__main__':
    bot.polling(none_stop=True)