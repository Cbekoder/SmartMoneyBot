import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor

# Initialize bot and dispatcher
bot = Bot(token='6509950356:AAFJJafE1FSW_Ty9bnwlCFSYjnXgWc2KuF8')
dp = Dispatcher(bot)

# Dictionary to store approved users
approved_users = set()
# Admin user ID (replace with your admin user ID)
ADMIN_USER_ID = 5729115581


# Command handler for /start command
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Welcome to the bot! Use /approve_me to get approved by the admin.")


# Command handler for /approve_me command
@dp.message_handler(commands=['approve_me'])
async def approve_me(message: types.Message):
    user_id = message.from_user.id
    if user_id == ADMIN_USER_ID:
        approved_users.add(user_id)
        await message.reply("You have been approved as admin.")
    else:
        await message.reply("Only admin can approve users.")


# Command handler for /send command (admin only)
@dp.message_handler(commands=['send'], user_id=ADMIN_USER_ID)
async def send_message_to_users(message: types.Message):
    if not approved_users:
        await message.reply("No users approved yet.")
        return

    text = message.text.split(' ', 1)[1]
    for user_id in approved_users:
        await bot.send_message(user_id, text)
    await message.reply(f"Message sent to {len(approved_users)} approved users.")


# Command handler for /send_photo command (admin only)
@dp.message_handler(commands=['send_photo'], user_id=ADMIN_USER_ID)
async def send_photo_to_users(message: types.Message):
    if not approved_users:
        await message.reply("No users approved yet.")
        return

    photo = message.photo[-1].file_id
    for user_id in approved_users:
        await bot.send_photo(user_id, photo)
    await message.reply(f"Photo sent to {len(approved_users)} approved users.")


# Error handler
@dp.errors_handler()
async def errors_handler(update, error):
    print(f'Update {update} caused error {error}')


# Start the bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
