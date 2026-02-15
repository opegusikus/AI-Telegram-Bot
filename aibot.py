from telebot.async_telebot import AsyncTeleBot
import os
from openai import OpenAI
from dotenv import load_dotenv
import textwrap
import re
import asyncio

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

bot = AsyncTeleBot(BOT_TOKEN, parse_mode=None)
client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.deepseek.com")

users = {}
#Maximum answer length is 2048 symbols.
final_instructions = ""
system_instructions = fr"""
Listen and obey all instructions here.
You are useful AI agent.
Next are user instructions if present:"""

def remember_user(message):
        #print('Im in remember user for {users[user_id]['username']}')
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

@bot.message_handler(commands=['start'])
async def send_welcome(message):
        remember_user(message)
        
        print(users)
        await bot.reply_to(message, """This is custom AI agent based on Deepseek.
Just write message normaly AI will answer.
List of all commands /help""")

@bot.message_handler(commands=['help'])
async def help(message):
        await bot.reply_to(message, """To write a prompt just send a message as you do normaly.
/custominstructions - write your preferences about responces etc to AI.
/help - this menu

""")

@bot.message_handler(commands=['custominstructions'])
async def user_settings(message):
        remember_user(message)
        user_id = message.chat.id
        users[user_id]['user_state'] = "waiting_for_instructions"
        await bot.reply_to(message, 'Now send your instructions to the AI agent')

def ask_ai(prompt):   
        response = client.chat.completions.create(
                model="deepseek-chat",
                #max_tokens=1024,
                temperature=0.3,
                messages=[
                        {"role": "system", "content": final_instructions},
                        {"role": "user", "content": prompt}
                        ],
                #stream=False
                )
        #print(response)
        return response.choices[0].message.content

#def escape_mdv2(text):
#       return re.sub(r'([_*\[\]~>#+\-=|(){}.!])', r'\\\1', text)

@bot.message_handler(content_types=['text'])
@bot.message_handler(func=lambda m: True)
async def handle_message(message):
        user_id = message.chat.id
        remember_user(message)
        print(f'Id: {message.chat.id}, user: {message.chat.username}, message: {message.text}')
        #print(message)
        #print(f'Im in message handler for {users[user_id]['username']}')
        if users[user_id]['user_state'] == "waiting_for_instructions":
                users[user_id]['instructions'] = message.text
                users[user_id]['user_state'] = None
                await bot.reply_to(message, "Instructions applied!")
                final_instructions = system_instructions + "\n" + users[user_id]['instructions']
                print(final_instructions)
                return
        answer = ask_ai(message.text)
        answer_length = len(answer)
        print(answer)
        chunk_size = 4096
        
        if answer_length >= chunk_size:
                chunks = [answer[i:i + chunk_size] for i in range(0, len(answer), chunk_size)]
                chunks = textwrap.wrap(answer, width=4096, break_long_words=False, replace_whitespace=False)
                #print(f'\nAI answered to user: {users[user_id]['name']}, language used: {users[user_id]['language']}')
                print(len(chunks))
                for i in range(0, len(chunks)):
                        await bot.reply_to(message, chunks[i])
        else:
                print(type(answer))
                await bot.reply_to(message, answer)
                
asyncio.run(bot.polling())
