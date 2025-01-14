import telebot
from config import TOKEN
import json

bot = telebot.TeleBot(TOKEN)

user_data = {}

#load questions from json file
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

questions = load_questions()

# Hello message
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Добро пожаловать в викторину о тотемных животных. Нажмите /quiz, чтобы начать!")

# Start quiz
@bot.message_handler(commands=['quiz'])
def start_quiz(message):
    user_data[message.chat.id] = {"current_question": 0, "total_score": 0}
    send_question(message.chat.id)

def send_question(chat_id):
    user_info = user_data.get(chat_id)
    if user_info["current_question"] < len(questions):
        question = questions[user_info["current_question"]]
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for option in question["options"]:
            markup.add(option)
        bot.send_message(chat_id, question["question"], reply_markup=markup)
    else:
        send_result(chat_id)

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

    #send result to user
    bot.send_message(chat_id, result)
    bot.send_message(chat_id, "Вы можете узнать больше о программе опеки на сайте зоопарка.")

    #delete user data
    del user_data[chat_id]

# bot start
if __name__ == '__main__':
    print("Бот запущен....")
    bot.infinity_polling()
