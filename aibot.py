import telebot
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.deepseek.com")

users = {}

final_instructions = ""
system_instructions = f"""
Listen and obey all instructions here.
You are useful AI agent.
Maximum answer length is 2048 symbols.
Next are user instructions if present:"""

def remember_user(message):
        #print('Im in remember user for {users[user_id][\'username\']}')
        user_id = message.chat.id

        if user_id not in users:
                users[user_id] = {
                        'username': None,
                        'instructions': '',
                        'user_state': None,
                        'language': None,
                        'tokens_today': None,
                        'history': None
                        }
                users[user_id]['username'] = message.chat.username
                users[user_id]['language'] = message.from_user.language_code
        return users

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
        remember_user(message)
        
        print(users)
        bot.reply_to(message, "This is custom AI agent based on Deepseek. Just write message normaly AI will answer. \nYou can input your custom instructions to this agent /custominstruction")

@bot.message_handler(commands=['custominstruction'])
def user_settings(message):
        remember_user(message)
        user_id = message.chat.id
        users[user_id]['user_state'] = "waiting_for_instructions"
        bot.reply_to(message, 'Now send your instructions to the AI agent')

def ask_ai(prompt):   
        response = client.chat.completions.create(
                model="deepseek-chat",
                max_tokens=1024,
                temperature=0.3,
                messages=[
                        {"role": "system", "content": final_instructions},
                        {"role": "user", "content": prompt}
                        ],
                #stream=False
                )
        #print(response)
        if type(response.choices[0].message.content) == 'str':
                print('\nAI answered')
        return response.choices[0].message.content

@bot.message_handler(content_types=['text'])
@bot.message_handler(func=lambda m: True)
def handle_message(message):
        user_id = message.chat.id
        remember_user(message)
        print(f'Id: {message.chat.id}, user: {message.chat.username}')
        #print(message)
        print(f'Im in message handler for {users[user_id][\'username\']}')
        if users[user_id]['user_state'] == "waiting_for_instructions":
                users[user_id]['instructions'] = message.text
                users[user_id]['user_state'] = None
                bot.reply_to(message, "Instructions applied!")
                final_instructions = system_instructions + "\n" + users[user_id]['instructions']
                print(final_instructions)
                return
        answer = ask_ai(message.text)
        bot.reply_to(message, answer)
        

bot.infinity_polling()
