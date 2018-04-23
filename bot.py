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
                                        "/" + "random - предложить случайную статью."+ '\n' +
                                        "/" + "choose_topic - выбрать тему, на которую бот предложит статьи.")


@bot.message_handler(commands=['random'])
def suggest_random_article(message):
    doc = artm_func.get_random_doc(theta)
    keyboard = types.InlineKeyboardMarkup()
    title = str(db.collection.find_one({'_id': doc})['title'])
    url = str(db.collection.find_one({'_id': doc})['url'])
    url_button = types.InlineKeyboardButton(text=title, url=url)
    keyboard.add(url_button)
    bot.send_message(message.chat.id, "Случайная статья:", reply_markup=keyboard)


@bot.message_handler(commands=['choose_topic'])
def suggest_topics(message):
    top_tokens = artm_func.get_top_tokens(model)
    keyboard = types.InlineKeyboardMarkup()
    print(top_tokens)
    for topic in top_tokens.keys():
        button = types.InlineKeyboardButton(text=str(top_tokens[topic]),
                                            callback_data=topic)
        keyboard.add(button)
    bot.send_message(message.chat.id,
                         "Выберите тему",
                         reply_markup=keyboard)



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


@bot.message_handler(content_types=['document'])
def suggest_5articles_from_doc(message):
    file_path = bot.get_file(message.document.file_id).file_path
    file = bot.download_file(file_path)
    doc_file = open(output_name, "wb")
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


chosen_topic = None

@bot.callback_query_handler(func=lambda call: call.data[:6] == 'topic_')
def get_topic(call):
    topic = call.data
    tokens = artm_func.get_top_tokens(model)[topic]
    doc_ids = artm_func.get_docs_ids_by_topic(topic)
    print(doc_ids)
    keyboard = types.InlineKeyboardMarkup()
    for doc in doc_ids.keys():
        title = str(db.collection.find_one({'_id': doc})['title'])
        url = str(db.collection.find_one({'_id': doc})['url'])
        url_button = types.InlineKeyboardButton(text=title, url=url)
        keyboard.add(url_button)
    bot.answer_callback_query(call.id, text="Тема выбрана!")
    bot.send_message(call.message.chat.id,
                     "Вот несколько статей на выбранную тему: "+str(tokens),
                     reply_markup=keyboard)


if __name__ == '__main__':
    bot.polling(none_stop=True)