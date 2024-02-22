import asyncio
import json
import logging
import aiogram
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ParseMode

# Load config
with open("config.json", "r") as file:
    config = json.load(file)

# Load users
with open("users.json", "r") as file:
    users = json.load(file)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config["token"])
dp = Dispatcher(bot)
admin_user_id = config["admins"][0]
stored_messages = []
sent_users = set()

# Command handlers
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    is_admin = str(message.from_user.id) in admin_user_id

    if is_admin:
        await message.answer(f"Salom {message.from_user.first_name}!\n\n"
                             "Sizda admin sifatida belgilangansiz."
                             "Foydalanish qo'llanmasini olish uchun\n"
                             "/help buyrug'idan foydalaning"
                             )
    else:
        await message.answer(f"Salom {message.from_user.first_name}.\n\n"
                             "Bu Smart Money kanali yordamchi boti.\n"
                             "Foydalanish qo'llanmasini olish uchun\n"
                             "/help buyrug'idan foydalaning"
                             )

@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    is_admin = str(message.from_user.id) in config["admin_ids"]

    if is_admin:
        await message.answer("Adminlar uchun quyidagi buyruqlar mavjud:\n"
                             "/signal - signallar qabul qilish\n"
                             "/send - signallarni yuborish\n"
                             )
    else:
        await message.answer("Bu botdan foydalanish va signallar qabul qila olishingiz uchun sizdan obuna bo'lish talab qilinadi.\n"
                             "Obuna bo'lish uchun adminga murojat qiling\n"
                             "admin: @SMART_MONE_ADMIN\n"
                             "va /subscribe buyrug'ini yuboring"
                             )


@dp.message_handler(commands=["add"])
async def add_user(message: types.Message):
    if str(message.from_user.id) in config["admin_ids"]:
        try:
            user_id = message.text.split()[1]
            user_id = int(user_id)
        except IndexError:
            await message.answer("Please provide a user id.")
            return
        except ValueError:
            await message.answer("Invalid user id.")
            return

        # Add user if not already in the list
        if user_id not in [int(user["id"]) for user in users]:
            users.append({"id": user_id, "allowed": True})
            with open("users.json", "w") as file:
                json.dump(users, file)
            await message.answer(f"User {user_id} added.")
        else:
            await message.answer(f"User {user_id} is already in the list.")
    else:
        await message.answer("You are not authorized to use this command.")


@dp.message_handler(commands=["ignore"])
async def ignore_user(message: types.Message):
    # Check if the user is admin
    if str(message.from_user.id) in config["admin_ids"]:
        # Get user_id to ignore
        try:
            user_id = message.text.split()[1]
            user_id = int(user_id)
        except IndexError:
            await message.answer("Please provide a user id.")
            return
        except ValueError:
            await message.answer("Invalid user id.")
            return

        # Ignore user if in the list
        for user in users:
            if user["id"] == user_id:
                user["allowed"] = False
                with open("users.json", "w") as file:
                    json.dump(users, file)
                await message.answer(f"User {user_id} ignored.")
                return

        await message.answer(f"User {user_id} is not in the list.")
    else:
        await message.answer("You are not authorized to use this command.")

@dp.message_handler(content_types=["photo"])
async def handle_photo(message: types.Message):
    # Check if the user is admin
    is_admin = str(message.from_user.id) in config["admin_ids"]

    if is_admin:
        await message.answer("This is a photo sent by an admin.")
        logging.info(message)
        return

    # Get user info
    user_info = f"{message.from_user.id}\n" \
                f"{message.from_user.full_name}\n" \
                f"@{message.from_user.username}"

    # Create inline keyboard
    keyboard = types.InlineKeyboardMarkup()
    add_button = types.InlineKeyboardButton(text="Add", callback_data="add")
    ignore_button = types.InlineKeyboardButton(text="Ignore", callback_data="ignore")
    keyboard.add(add_button, ignore_button)

    # Send message to admin
    admin_message = await message.answer_photo(photo=message.photo[-1].file_id,
                                               caption=f"New user photo\n"
                                                       f"Comment: {message.caption}\n"
                                                       f"{user_info}",
                                               reply_markup=keyboard)
    await bot.send_message(config["admin_ids"][0], f"New user found: {message.from_user.full_name}")

    # Notify the user
    await message.answer("Your request is pending approval.")


@dp.message_handler(commands=['signal'], user_id=admin_user_id)
async def handle_signal_command(message: types.Message):
    global signal_mode
    signal_mode = True
    await message.answer("Please send any messages to send to subscribers or tap /send to finish.")

@dp.message_handler(commands=['send'], user_id=admin_user_id)
async def handle_send_command(message: types.Message):
    global signal_mode
    if signal_mode:
        signal_mode = False
        await message.answer("Your messages have been sent to subscribers.")
        # Send all stored messages to allowed users
        for stored_message in stored_messages:
            for user in [int(user["id"]) for user in users]:
                user_id = user
                # Check if the message has been sent to this user before
                if user_id not in sent_users:
                    try:
                        await bot.send_message(user_id, stored_message)
                        logging.info(f"Message forwarded to user {user_id}")
                        sent_users.add(user_id)  # Add the user ID to sent_users set
                    except Exception as e:
                        logging.error(f"Failed to forward message to user {user_id}: {e}")
            sent_users.clear()
        stored_messages.clear()
    else:
        await message.answer("You haven't initiated the signal mode yet.")


@dp.message_handler(user_id=admin_user_id)
async def handle_admin_message(message: types.Message):
    if signal_mode:
        stored_messages.append(message)
        logging.info(message)
        await message.answer("Message received. Please send another message or tap /send to finish.")
    else:
        await message.answer("Please use /signal command to initiate the message sending process.")

# Inline keyboard handler
@dp.callback_query_handler(lambda c: c.data in ["add", "ignore"])
async def process_callback(callback_query: types.CallbackQuery):
    # Check if the user is admin
    is_admin = str(callback_query.from_user.id) in config["admin_ids"]

    if not is_admin:
        await callback_query.answer("You are not authorized to use this command.", show_alert=True)
        return

    # Delete original message
    await callback_query.message.delete()

    # Respond to the button click
    if callback_query.data == "add":
        await callback_query.message.answer("User is added.")
    elif callback_query.data == "ignore":
        await callback_query.message.answer("User is ignored.")


async def on_startup(dp):
    await bot.send_message(config["admin_ids"][0], "Bot started.")


if __name__ == "__main__":
    # Start the bot
    executor.start_polling(dp, skip_updates=True)
