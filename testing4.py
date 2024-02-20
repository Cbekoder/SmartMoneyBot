import json
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config['token'])
dp = Dispatcher(bot)

# Load users from JSON
with open("users.json", "r") as f:
    users = json.load(f)

# Save users to JSON
def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# Admin ID
admin_id = config['admin_id']

# Start command handler
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id != admin_id:
        await bot.send_message(admin_id, f"New User found\n"
                                          f"id: {message.from_user.id}\n"
                                          f"name: {message.from_user.full_name}\n"
                                          f"username: {message.from_user.username}\n"
                                          f"started at: {message.date}\n"
                                          f"allowed: False")
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Add", callback_data=f"add_{user_id}"))
        keyboard.add(types.InlineKeyboardButton(text="Ignore", callback_data=f"ignore_{user_id}"))
        await message.reply("Do you allow this user?", reply_markup=keyboard)
    else:
        await message.reply("Welcome Admin!")

# Callback handler for add or ignore user
@dp.callback_query_handler(lambda callback_query: True)
async def handle_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.data.split('_')[1]
    if "add" in callback_query.data:
        users.append({"id": user_id, "allowed": True})
        save_users()
        await callback_query.answer("User added.")
    elif "ignore" in callback_query.data:
        await bot.send_message(int(user_id), "You are not allowed to access this bot.")

# Signal command handler
@dp.message_handler(commands=['signal'])
async def signal(message: types.Message):
    if str(message.from_user.id) == admin_id:
        await message.reply("Please send any messages to send to subscribers")

# Send command handler
@dp.message_handler(commands=['send'])
async def send(message: types.Message):
    if str(message.from_user.id) == admin_id:
        await message.reply("Your below messages sent to subscribers")
        async for msg in message.chat.history():
            if msg.text and msg.text.startswith("/signal"):
                continue
            await asyncio.sleep(0.1)  # To avoid flooding
            for user in users:
                if user["allowed"]:
                    try:
                        await bot.send_message(user["id"], msg.text)
                    except Exception as e:
                        logging.error(f"Error sending message to {user['id']}: {e}")

# Handle text messages from admin
@dp.message_handler(lambda message: str(message.from_user.id) == admin_id and not message.text.startswith("/"))
async def forward_message(message: types.Message):
    async for msg in message.chat.history():
        if msg.text and msg.text.startswith("/signal"):
            continue
        await asyncio.sleep(0.1)  # To avoid flooding
        for user in users:
            if user["allowed"]:
                try:
                    await bot.send_message(user["id"], msg.text)
                except Exception as e:
                    logging.error(f"Error sending message to {user['id']}: {e}")

# Error handler
@dp.errors_handler()
async def error_handler(update, exception):
    logging.exception(f"Exception: {exception}")
    await update.message.reply("An error occurred.")

# Start the bot
async def on_startup(dp):
    logging.info("Starting bot")
    await bot.set_my_commands([
        types.BotCommand("start", "Start the bot"),
        types.BotCommand("signal", "Signal the subscribers"),
        types.BotCommand("send", "Send messages to subscribers")
    ])

# Shutdown the bot
async def on_shutdown(dp):
    logging.info("Shutting down bot")

if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=on_shutdown, skip_updates=True)
