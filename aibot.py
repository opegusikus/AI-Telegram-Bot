import telebot
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.deepseek.com")

user_instructions = {}
user_state = {}
final_instructions = ""
system_instructions = f"""
Listen all and obey all instructions here.
You are useful AI agent.
        """

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
        bot.reply_to(message, "This is custom AI agent based on Deepseek. \nYou can input your custom instructions to this agent /customInstruction")

@bot.message_handler(commands=['customInstruction'])
def user_settings(message):
        user_id = message.chat.id
        user_state[user_id] = "waiting_for_instructions"
        bot.reply_to(message, 'Now send your instructions to the AI agent')

def ask_ai(prompt):
        
        
        response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                        {"role": "system", "content": final_instructions},
                        {"role": "user", "content": prompt}
                        ],
                #stream=False
                )
        print(response)
        return response.choices[0].message.content

@bot.message_handler(content_types=['text'])
@bot.message_handler(func=lambda m: True)
def handle_message(message):
        user_id = message.chat.id
        if user_state.get(user_id) == "waiting_for_instructions":
                user_instructions = message.text
                user_state[user_id] = None
                bot.reply_to(message, "Instructions applied!")
                final_instructions = system_instructions + "\n" + user_instructions
                print(final_instructions)
                return
        answer = ask_ai(message.text)
        bot.reply_to(message, answer)
        

bot.infinity_polling()
