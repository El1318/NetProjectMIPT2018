import config
import artm_model
import db
import telebot
import pandas
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
    response, values = artm_model.transform(model, "message.txt", 'filename')
    doc_ids = values[0] * artm_model.get_docs_ids_by_topic(theta, response[0])
    for i in range(1,5):
       doc_ids = pandas.concat([doc_ids, values[i]*artm_model.get_docs_ids_by_topic(theta, response[i])])
    doc_ids = doc_ids.sort_values(ascending=False)
    print(str(doc_ids))
    response = ''
    for doc in doc_ids.keys()[:5]:
        response += str(db.collection.find_one({'_id': doc}, projection = ['title', 'url']))
        response += '\n'
    bot.send_message(message.chat.id, str(response))


if __name__ == '__main__':
    bot.polling(none_stop=True)