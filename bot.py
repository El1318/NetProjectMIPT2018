import config
import artm_func
import db
import telebot
from telebot import apihelper
from telebot import types

bot = telebot.TeleBot(config.token)
if config.proxy == True:
    proxy = config.proxy_settings()
    apihelper.proxy = {'https':'socks5://'+proxy.user+":"+proxy.password+"@"+proxy.address+":"+proxy.port}

model = artm_func.model
theta = artm_func.theta
output_name = "message.txt"

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    bot.send_message(message.chat.id, "Введите текст для поиска статей на похожие темы." + '\n' +
                                        "Также можно отправить текстовый документ." + '\n' +
                                        "/" + "random - предложить случайную статью.")

@bot.message_handler(commands=['random'])
def suggest_random_article(message):
    doc = artm_func.get_random_doc(theta)
    keyboard = types.InlineKeyboardMarkup()
    title = str(db.collection.find_one({'_id': doc})['title'])
    url = str(db.collection.find_one({'_id': doc})['url'])
    url_button = types.InlineKeyboardButton(text=title, url=url)
    keyboard.add(url_button)
    bot.send_message(message.chat.id, "Случайная статья:", reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def suggest_5articles_from_text(message):
    doc_file = open(output_name, "w")
    doc_file.write(message.text)
    doc_file.close()
    doc_ids = artm_func.get_top_docs(model, output_name)
    keyboard = types.InlineKeyboardMarkup()
    for doc in doc_ids.keys()[:5]:
        title = str(db.collection.find_one({'_id': doc})['title'])
        url = str(db.collection.find_one({'_id': doc})['url'])
        url_button = types.InlineKeyboardButton(text=title, url=url)
        keyboard.add(url_button)
    bot.send_message(message.chat.id, "В этих статьях может быть что-то похожее:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.document.mime_type == 'text/plain', content_types=['document'])
def suggest_5articles_from_doc(message):
    file_path = bot.get_file(message.document.file_id).file_path
    file = bot.download_file(file_path)
    doc_file = open(output_name, "w")
    doc_file.write(file)
    doc_file.close()
    doc_ids = artm_func.get_top_docs(model, output_name)
    keyboard = types.InlineKeyboardMarkup()
    for doc in doc_ids.keys()[:5]:
        title = str(db.collection.find_one({'_id': doc})['title'])
        url = str(db.collection.find_one({'_id': doc})['url'])
        url_button = types.InlineKeyboardButton(text=title, url=url)
        keyboard.add(url_button)
    bot.send_message(message.chat.id, "В этих статьях может быть что-то похожее:", reply_markup=keyboard)

if __name__ == '__main__':
    bot.polling(none_stop=True)