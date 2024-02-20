from telegram import Update, Filters
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext

# Define a dictionary to store approved users
approved_users = {}

# Define admin user ID (replace with your admin user ID)
ADMIN_USER_ID = 123456789

# Command handler for /start command
def start(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! I'm the bot. Use /help to see available commands.")

# Command handler for /help command
def help(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Available commands:\n/approve <user_id>\n/revoke <user_id>\n/send <user_id> <message>\n/send_photo <user_id> <photo_url>")

# Command handler for /approve command
def approve(update: Update, context: CallbackContext) -> None:
    user_id = int(context.args[0])
    approved_users[user_id] = True
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"User {user_id} approved.")

# Command handler for /revoke command
def revoke(update: Update, context: CallbackContext) -> None:
    user_id = int(context.args[0])
    if user_id in approved_users:
        del approved_users[user_id]
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Approval revoked for user {user_id}.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"User {user_id} was not approved.")

# Command handler for /send command
def send_message(update: Update, context: CallbackContext) -> None:
    if len(context.args) >= 2:
        user_id = int(context.args[0])
        message = ' '.join(context.args[1:])
        if user_id in approved_users:
            context.bot.send_message(chat_id=user_id, text=message)
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Message sent to user {user_id}.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"User {user_id} is not approved.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid command. Usage: /send <user_id> <message>")

# Command handler for /send_photo command
def send_photo(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 2:
        user_id = int(context.args[0])
        photo_url = context.args[1]
        if user_id in approved_users:
            context.bot.send_photo(chat_id=user_id, photo=photo_url)
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Photo sent to user {user_id}.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"User {user_id} is not approved.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid command. Usage: /send_photo <user_id> <photo_url>")

# Message handler for regular messages
def echo(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm just a bot. I only respond to commands.")

# Error handler
def error(update: Update, context: CallbackContext) -> None:
    print(f"Update {update} caused error {context.error}")

def main() -> None:
    # Initialize the updater and pass your bot's token
    updater = Updater(token='YOUR_BOT_TOKEN', use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("approve", approve))
    dp.add_handler(CommandHandler("revoke", revoke))
    dp.add_handler(CommandHandler("send", send_message))
    dp.add_handler(CommandHandler("send_photo", send_photo))

    # Message handler for regular messages
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Error handler
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you send a signal to stop it
    updater.idle()

if __name__ == '__main__':
    main()
