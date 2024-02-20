import json
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

# Replace 'YOUR_TOKEN' with your actual bot token
API_TOKEN = '6509950356:AAFJJafE1FSW_Ty9bnwlCFSYjnXgWc2KuF8'

admin_id = 5729115581

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


# Define states for admin message sending
class AdminStates(StatesGroup):
    awaiting_action = State()


# Load allowed users from JSON
def load_allowed_users():
    try:
        with open("allowed_users.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


# Save allowed users to JSON
def save_allowed_users(allowed_users):
    with open("allowed_users.json", "w") as file:
        json.dump(allowed_users, file, indent=4)


# Command for admin to start message sending
@dp.message_handler(commands=['signal'], user_id=admin_id)
async def cmd_signal(message: types.Message):
    await message.answer("Please send any messages or files you want to send to subscribers.")


# Handler for messages or files sent by admin
@dp.message_handler(state=AdminStates.awaiting_action, user_id=admin_id)
async def process_message_from_admin(message: types.Message, state: FSMContext):
    await state.update_data(messages=[])
    async with state.proxy() as data:
        if message.text == '/send':
            await send_messages_to_subscribers(message, data['messages'])
            await state.finish()
        else:
            data['messages'].append(message)
            await message.answer("Send another message or file or tap /send to send to subscribers.")


# Command for admin to allow a new user
@dp.message_handler(commands=['allow'], user_id=admin_id)
async def allow_new_user(message: types.Message):
    # Extract user info from message
    user_info = message.get_args().splitlines()
    new_user_id = user_info[0]
    new_user_name = user_info[1]
    new_user_username = user_info[2]

    # Add new user to allowed list
    allowed_users.append({"id": new_user_id, "allowed": True})
    save_allowed_users(allowed_users)

    await message.answer(f"User {new_user_name} ({new_user_username}) is allowed to receive your messages.")


# Command for admin to ignore a new user
@dp.message_handler(commands=['ignore'], user_id=admin_id)
async def ignore_new_user(message: types.Message):
    await message.answer("User ignored.")


# Handler for new users
@dp.message_handler(commands=['start'])
async def new_user(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    user_username = message.from_user.username

    # Notify admin about new user
    await bot.send_message(admin_id, f"New user found:\n"
                                      f"id: {user_id}\n"
                                      f"name: {user_name}\n"
                                      f"username: {user_username}\n"
                                      f"started at: {message.date}\n"
                                      f"allowed: False\n"
                                      f"Do you allow this user?", reply_markup=types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="/allow"),
                types.KeyboardButton(text="/ignore")
            ]
        ],
        resize_keyboard=True
    ))


# Function to send messages to subscribers
async def send_messages_to_subscribers(message: types.Message, messages: list):
    for msg in messages:
        if msg.content_type == 'text':
            await bot.send_message(msg.text, message.text)
        elif msg.content_type == 'photo':
            await bot.send_photo(msg.text, msg.photo[-1].file_id)
        # Add other types of messages as needed


if __name__ == '__main__':
    # Load admin and allowed users' IDs
    admin_id = 5729115581
    allowed_users = load_allowed_users()
    dp.loop.create_task(bot.send_message(admin_id, "Bot started"))

    # Start long-polling
    try:
        from aiogram import executor
        executor.start_polling(dp, skip_updates=True)
    finally:
        # Close the bot connection
        dp.loop.run_until_complete(bot.close())
