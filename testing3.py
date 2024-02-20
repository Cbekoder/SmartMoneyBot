import json
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# Replace 'YOUR_TOKEN' with your actual bot token
API_TOKEN = '6509950356:AAFJJafE1FSW_Ty9bnwlCFSYjnXgWc2KuF8'
admin_id = 5729115581

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Path to the JSON file to store allowed users
USERS_JSON_FILE = "allowed_users.json"


# Load allowed users from JSON
def load_allowed_users():
    try:
        with open(USERS_JSON_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


# Save allowed users to JSON
def save_allowed_users(allowed_users):
    with open(USERS_JSON_FILE, "w") as file:
        json.dump(allowed_users, file, indent=4)


# Define states for admin message sending
class AdminStates(StatesGroup):
    awaiting_signal = State()
    awaiting_send = State()


# Command for admin to start message sending
@dp.message_handler(commands=['signal'], user_id=admin_id)
async def cmd_signal(message: types.Message):
    await message.answer("Please send any messages or files you want to send to subscribers.")
    await AdminStates.awaiting_send.set()


# Handler for messages or files sent by admin
@dp.message_handler(state=AdminStates.awaiting_send, user_id=admin_id)
async def process_message_from_admin(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == '/send':
            await send_messages_to_subscribers(data['messages'])
            await state.finish()
        else:
            data['messages'].append(message)
            await message.answer("Send another message or file or tap /send to send to subscribers.")


# Command for admin to add a new user
@dp.message_handler(commands=['add'], user_id=admin_id)
async def add_new_user(message: types.Message):
    user_id = message.get_args()
    allowed_users = load_allowed_users()
    allowed_users.append({"id": user_id, "allowed": True})
    save_allowed_users(allowed_users)
    await message.answer(f"User {user_id} added to the allowed users.")


# Command for admin to ignore a new user
@dp.message_handler(commands=['ignore'], user_id=admin_id)
async def ignore_new_user(message: types.Message):
    user_id = message.get_args()
    allowed_users = load_allowed_users()
    for user in allowed_users:
        if user['id'] == user_id:
            user['allowed'] = False
            break
    save_allowed_users(allowed_users)
    await message.answer(f"User {user_id} ignored.")


# Handler for new users
@dp.message_handler(commands=['start'])
async def new_user(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    user_username = message.from_user.username
    starting_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Notify admin about new user
    keyboard = types.InlineKeyboardMarkup()
    add_button = types.InlineKeyboardButton("Add", callback_data=f"add_{user_id}")
    ignore_button = types.InlineKeyboardButton("Ignore", callback_data=f"ignore_{user_id}")
    keyboard.add(add_button, ignore_button)
    await bot.send_message(admin_id, f"New user found:\n"
                                      f"id: {user_id}\n"
                                      f"name: {user_name}\n"
                                      f"username: {user_username}\n"
                                      f"starting time: {starting_time}\n"
                                      f"Do you allow this user?", reply_markup=keyboard)


# Function to send messages to subscribers
async def send_messages_to_subscribers(messages: list):
    allowed_users = load_allowed_users()
    for user in allowed_users:
        if user['allowed']:
            for msg in messages:
                await bot.forward_message(user['id'], from_chat_id=admin_id, message_id=msg.message_id)


# Handler for callback queries (add/ignore user)
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith(('add_', 'ignore_')), user_id=admin_id)
async def handle_callback_query(callback_query: types.CallbackQuery):
    user_id = callback_query.data.split('_')[-1]
    if callback_query.data.startswith('add_'):
        allowed_users = load_allowed_users()
        allowed_users.append({"id": user_id, "allowed": True})
        save_allowed_users(allowed_users)
        await bot.answer_callback_query(callback_query.id, text=f"User {user_id} added to allowed users.")
    elif callback_query.data.startswith('ignore_'):
        allowed_users = load_allowed_users()
        for user in allowed_users:
            if user['id'] == user_id:
                user['allowed'] = False
                break
        save_allowed_users(allowed_users)
        await bot.answer_callback_query(callback_query.id, text=f"User {user_id} ignored.")


if __name__ == '__main__':
    # Replace 'YOUR_ADMIN_ID' with your actual admin user ID
    admin_id = 5729115581
    executor.start_polling(dp, skip_updates=True)

