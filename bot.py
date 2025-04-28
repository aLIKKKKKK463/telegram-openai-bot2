import os
import openai
import telebot
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize bot and OpenAI
bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# Dictionary to store user histories
user_histories = defaultdict(list)

def ask_openai(user_id, user_message):
    history = user_histories[user_id]
    history.append({"role": "user", "content": user_message})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Ты дружелюбный Telegram-бот, который отвечает на вопросы пользователя на русском языке."}, *history],
        temperature=0.7,
        max_tokens=500,
    )
    answer = response.choices[0].message["content"]
    history.append({"role": "assistant", "content": answer})
    if len(history) > 20:
        history = history[-20:]
    user_histories[user_id] = history
    return answer

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    bot.send_chat_action(user_id, 'typing')
    reply = ask_openai(user_id, message.text)
    bot.send_message(user_id, reply)

if __name__ == "__main__":
    bot.infinity_polling()