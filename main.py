import telebot
from config import TOKEN, STAFF_CHAT_ID
import json
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

bot = telebot.TeleBot(TOKEN)

user_data = {}

# Load questions from a JSON file
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

questions = load_questions()

# Welcome message
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    quiz_button = KeyboardButton("Пройти викторину")
    info_button = KeyboardButton("Узнать о программе опеки")
    markup.add(quiz_button, info_button)

    bot.send_message(
        message.chat.id,
        "Привет! Добро пожаловать в бот Московского зоопарка. Вы можете пройти викторину или узнать больше о программе опеки.",
        reply_markup=markup
    )

# Start quiz (via command or button)
@bot.message_handler(commands=['quiz'])
@bot.message_handler(func=lambda message: message.text == "Пройти викторину")
def start_quiz(message):
    user_data[message.chat.id] = {"current_question": 0, "total_score": 0}
    send_question(message.chat.id)

# Send a quiz question
def send_question(chat_id):
    user_info = user_data.get(chat_id)
    if not user_info or "current_question" not in user_info:
        bot.send_message(chat_id, "Ошибка: невозможно продолжить викторину.")
        return

    if user_info["current_question"] < len(questions):
        question = questions[user_info["current_question"]]
        markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for option in question["options"]:
            markup.add(option)
        bot.send_message(chat_id, question["question"], reply_markup=markup)
    else:
        send_result(chat_id)


# Handle quiz answers
@bot.message_handler(func=lambda message: message.chat.id in user_data)
def handle_answer(message):
    user_info = user_data[message.chat.id]

    if user_info["current_question"] < len(questions):
        question = questions[user_info["current_question"]]
        if message.text in question["options"]:
            index = question["options"].index(message.text)
            user_info["total_score"] += question["scores"][index]
            user_info["current_question"] += 1
            send_question(message.chat.id)
        else:
            bot.reply_to(message, "Пожалуйста, выберите один из предложенных вариантов.")
    else:
        send_result(message.chat.id)


# Show quiz result
def send_result(chat_id):
    if chat_id not in user_data:
        return

    score = user_data[chat_id]["total_score"]
    if score <= 5:
        result = "Ваше тотемное животное - Ушастый ёж!"
        image_path = "images/hedgehog.jpeg"
    elif score <= 8:
        result = "Ваше тотемное животное - Обыкновенная Лисица!"
        image_path = "images/fox.jpg"
    else:
        result = "Ваше тотемное животное - Малайский Медведь!"
        image_path = "images/bear.jpg"

    with open(image_path, "rb") as photo:
        bot.send_photo(chat_id, photo)

    show_result(chat_id, result)

# Display result and offer retry
def show_result(chat_id, result):
    bot.send_message(chat_id, result)

    share_markup = InlineKeyboardMarkup()

#Telegram
    telegram_button = InlineKeyboardButton(
        text="Поделиться в Telegram",
        url=f"https://t.me/share/url?url=https://t.me/{bot.get_me().username}&text={result}"
    )
    share_markup.add(telegram_button)

#WhatsApp
    whatsapp_button = InlineKeyboardButton(
        text="Поделиться в WhatsApp",
        url=f"https://api.whatsapp.com/send?text={result}%20https://t.me/{bot.get_me().username}"
    )
    share_markup.add(whatsapp_button)

#Facebook
    facebook_button = InlineKeyboardButton(
        text="Поделиться в Facebook",
        url=f"https://www.facebook.com/sharer/sharer.php?u=https://t.me/{bot.get_me().username}&quote={result}"
    )
    share_markup.add(facebook_button)

#Twitter
    twitter_button = InlineKeyboardButton(
        text="Поделиться в Twitter",
        url=f"https://twitter.com/intent/tweet?text={result}&url=https://t.me/{bot.get_me().username}"
    )
    share_markup.add(twitter_button)

#Send message with buttons
    bot.send_message(
        chat_id,
        "Хотите поделиться результатом с друзьями в социальных сетях?",
        reply_markup=share_markup
    )

    retry_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    retry_markup.add("Попробовать ещё раз", "Узнать о программе опеки", "Связаться с сотрудником зоопарка")
    bot.send_message(chat_id, "Что вы хотите сделать дальше?", reply_markup=retry_markup)

# #delete user data
#     del user_data[chat_id]

# Retry quiz
@bot.message_handler(func=lambda message: message.text == "Попробовать ещё раз")
def retry_quiz(message):
    start_quiz(message)

# Provide information about adoption program
@bot.message_handler(commands=['about'])
@bot.message_handler(func=lambda message: message.text == "Узнать о программе опеки")
def send_about_info(message):
    about_text = (
        "Программа опеки помогает заботиться о животных зоопарка. "
        "Вы можете стать опекуном любого животного и поддерживать его. "
        "Подробнее о программе опеки можно узнать на нашем сайте.\n\n"
        "👉 [Подробнее о программе опеки](https://example.com/adoption)\n"
        "👉 [Хочешь стать опекуном, напиши нам! zoofriends@moscowzoo.ru]\n\n"
        "Спасибо за вашу поддержку! ❤️"
    )
    bot.send_message(message.chat.id, about_text, parse_mode="Markdown")

#Contact stuff
@bot.message_handler(func=lambda message: message.text == "Связаться с сотрудником зоопарка")
def contact_staff(message):
    bot.send_message(
        message.chat.id,
        "Пожалуйста, напишите ваш вопрос или запрос, и мы передадим его сотруднику. "
        "Не забудьте уточнить, с каким животным связан ваш вопрос!"
    )
    bot.register_next_step_handler(message, forward_to_staff)

def forward_to_staff(message):
    user_result = user_data.get(message.chat.id, {}).get("total_score", "Результат не найден")
    result_text = f"Пользователь @{message.from_user.username or 'без имени'}:\n"
    result_text += f"Результат викторины: {user_result}\n"
    result_text += f"Сообщение: {message.text}"

#Send message to staff
    bot.send_message(STAFF_CHAT_ID, result_text)
    bot.reply_to(message, "Ваш запрос был отправлен сотруднику. Спасибо!")
    if message.chat.id in user_data:
        del user_data[message.chat.id]


# Collect user feedback
@bot.message_handler(commands=['feedback'])
def feedback_handler(message):
    bot.send_message(message.chat.id, "Напишите ваш отзыв. Мы будем рады вашим предложениям!")
    bot.register_next_step_handler(message, save_feedback)

def save_feedback(message):
    with open("feedback.txt", "a", encoding="utf-8") as f:
        f.write(f"От {message.chat.id}: {message.text}\n")
    bot.reply_to(message, "Спасибо за ваш отзыв!")

# Start the bot
if __name__ == '__main__':
    print("Бот запущен....")
    bot.infinity_polling()
