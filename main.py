import telebot
from config import TOKEN
import json
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

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
    question = questions[user_info["current_question"]]
    if message.text in question["options"]:
        index = question["options"].index(message.text)
        user_info["total_score"] += question["scores"][index]
        user_info["current_question"] += 1
        send_question(message.chat.id)
    else:
        bot.reply_to(message, "Пожалуйста, выберите один из предложенных вариантов.")

# Show quiz result
def send_result(chat_id):
    if chat_id not in user_data:
        return

    score = user_data[chat_id]["total_score"]
    if score <= 5:
        result = "Ваше тотемное животное - Ежик! 🦔"
    elif score <= 8:
        result = "Ваше тотемное животное - Лиса! 🦊"
    else:
        result = "Ваше тотемное животное - Медведь! 🐻"

    show_result(chat_id, result)

# Display result and offer retry
def show_result(chat_id, result):
    bot.send_message(chat_id, result)
    retry_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    retry_markup.add("Попробовать ещё раз")
    bot.send_message(chat_id, "Хотите попробовать ещё раз?", reply_markup=retry_markup)

    del user_data[chat_id]

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
