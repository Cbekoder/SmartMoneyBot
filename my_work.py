import json
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware

API_TOKEN = '6509950356:AAFJJafE1FSW_Ty9bnwlCFSYjnXgWc2KuF8'
admin_id = 5729115581

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

json_list = "users_list"

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_username = message.from_user.username
    starting_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user_id == admin_id:
        await message.answer(f"Assalomu alaykum {user_name}, Boshqaruvingizdadi signallar uchun botga hush kelibsiz.\nFoydalanish qollanmasini olish uchun /help buyrug'idan foydalaning.")
        
