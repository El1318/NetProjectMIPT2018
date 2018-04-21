import config
import artm_model
import db
import telebot
import pandas
from telebot import apihelper
from telebot import types

bot = telebot.TeleBot(config.token)
if config.proxy == True:
    proxy = config.proxy_settings()
    apihelper.proxy = {'https':'socks5://'+proxy.user+":"+proxy.password+"@"+proxy.address+":"+proxy.port}

model = artm_model.model
theta = artm_model.theta
output_name = "message.txt"

@bot.message_handler(content_types=["text"])
def suggest_5articles(message):
    doc_file = open(output_name, "w")
    doc_file.write(message.text)
    doc_file.close()
    doc_ids = artm_model.get_top_docs(model, output_name)
    print(str(doc_ids))
    keyboard = types.InlineKeyboardMarkup()
    for doc in doc_ids.keys()[:5]:
        title = str(db.collection.find_one({'_id': doc})['title'])
        url = str(db.collection.find_one({'_id': doc})['url'])
        url_button = types.InlineKeyboardButton(text=title, url=url)
        keyboard.add(url_button)
    bot.send_message(message.chat.id, "В этих статьях может быть что-то похожее:", reply_markup=keyboard)


if __name__ == '__main__':
    bot.polling(none_stop=True)