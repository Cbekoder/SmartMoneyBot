import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor

# Initialize bot and dispatcher
bot = Bot(token='6509950356:AAFJJafE1FSW_Ty9bnwlCFSYjnXgWc2KuF8')
dp = Dispatcher(bot)

# Dictionary to store approved users and their permissions
user_permissions = {}

# Admin user ID (replace with your admin user ID)
ADMIN_USER_ID = 5729115581

# Command handler for /start command
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Welcome to the bot! Use /add_me to allow receiving messages from the admin.")

# Command handler for /add_me command
@dp.message_handler(commands=['add_me'])
async def add_me(message: types.Message):
    user_id = message.from_user.id
    user_permissions[user_id] = True
    await message.reply("You will now receive messages from the admin.")

# Command handler for /ignore_me command
@dp.message_handler(commands=['ignore_me'])
async def ignore_me(message: types.Message):
    user_id = message.from_user.id
    user_permissions[user_id] = False
    await message.reply("You will no longer receive messages from the admin.")

# Command handler for admin to add user permissions
@dp.message_handler(commands=['add'], user_id=ADMIN_USER_ID)
async def add_permissions(message: types.Message):
    user_id = int(message.text.split(' ', 1)[1])
    user_permissions[user_id] = True
    await message.reply(f"User {user_id} has been granted permission to receive messages from the admin.")

# Command handler for admin to ignore user permissions
@dp.message_handler(commands=['ignore'], user_id=ADMIN_USER_ID)
async def ignore_permissions(message: types.Message):
    user_id = int(message.text.split(' ', 1)[1])
    user_permissions[user_id] = False
    await message.reply(f"User {user_id} has been ignored and will not receive messages from the admin.")

# Message handler for regular messages from admin
@dp.message_handler(lambda message: message.from_user.id == ADMIN_USER_ID and message.text.startswith('/send'))
async def send_message_to_user(message: types.Message):
    _, user_id, text = message.text.split(' ', 2)
    user_id = int(user_id)
    if user_id not in user_permissions:
        await message.reply("User's permission not set.")
        return
    if not user_permissions[user_id]:
        await message.reply("User has been ignored and will not receive messages from the admin.")
        return
    await bot.send_message(user_id, text)
    await message.reply(f"Message sent to user {user_id}.")

# Error handler
@dp.errors_handler()
async def errors_handler(update, error):
    print(f'Update {update} caused error {error}')

# Start the bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
