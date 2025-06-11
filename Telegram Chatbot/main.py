from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher, executor, types
import requests
import openai
import sys

load_dotenv()
api_token = os.getenv("EURON_API_TOKEN")  # Euron API token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

class Reference:
    '''
    A class to store previously response from the API
    '''
    def __init__(self) -> None:
        self.response = ""

reference = Reference()
model_name = "gpt-4.1-nano"  # Model provided by Euron

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot)

def clear_past():
    """A function to clear the previous conversation and context."""
    reference.response = ""

@dispatcher.message_handler(commands=['clear'])
async def clear(message: types.Message):
    """A handler to clear the previous conversation and context."""
    clear_past()
    await message.reply("I've cleared the past conversation and context.")

@dispatcher.message_handler(commands=['start'])
async def welcome(message: types.Message):
    """Handler for /start command."""
    await message.reply("Hi\nI am Tele Bot!\nCreated by Akash. How can I assist you?")

@dispatcher.message_handler(commands=['help'])
async def helper(message: types.Message):
    """Handler for /help command."""
    help_command = """
    Hi There, I'm Telegram bot created by Akash! Please follow these commands - 
    /start - to start the conversation
    /clear - to clear the past conversation and context.
    /help - to get this help menu.
    I hope this helps. :)
    """
    await message.reply(help_command)

@dispatcher.message_handler()
async def chatgpt(message: types.Message):
    """Handles user input and generates a response using Euron's OpenAI proxy."""
    print(f">>> USER: \n\t{message.text}")
    
    try:
        # Prepare the message history
        messages = []
        if reference.response:
            messages.append({"role": "assistant", "content": reference.response})
        messages.append({"role": "user", "content": message.text})

        # Call Euron's API
        response = requests.post(
            url="https://api.euron.one/api/v1/euri/alpha/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_token}",
            },
            json={
                "model": model_name,
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.6,
                "n": 1
            }
        )

        data = response.json()
        
        # Handle response
        if "choices" in data and len(data["choices"]) > 0:
            reply = data["choices"][0]["message"]["content"]
            reference.response = reply
            print(f">>> chatGPT: \n\t{reply}")
            await bot.send_message(chat_id=message.chat.id, text=reply)
        else:
            print("Error: Unexpected response structure", data)
            await bot.send_message(chat_id=message.chat.id, text="Sorry, I couldn't understand the response.")
    except Exception as e:
        print("Exception:", e)
        await bot.send_message(chat_id=message.chat.id, text="Something went wrong!")

if __name__ == "__main__":
    executor.start_polling(dispatcher, skip_updates=False)
