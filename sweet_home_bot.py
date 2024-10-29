import time
#import schedule
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import mqtt_control

# Replace with your bot token
BOT_TOKEN = ''

# Initialize the bot and the set of subscribed users
bot = Bot(token=BOT_TOKEN)
subscribed_users = set()

# Function to send periodic messages only to subscribed users
def send_periodic_message():
    send_message("Hello! This is your periodic message.")

def send_message(msg):
    print(msg)
    for chat_id in subscribed_users:
        bot.send_message(chat_id=chat_id, text=msg)

# Start command handler to display the subscription menu
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    # Define the inline keyboard
    keyboard = [
        [InlineKeyboardButton("Subscribe", callback_data='subscribe')],
        [InlineKeyboardButton("Unsubscribe", callback_data='unsubscribe')],
        [InlineKeyboardButton("Details", callback_data='details')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send the menu
    context.bot.send_message(chat_id=chat_id, text="Choose an option:", reply_markup=reply_markup)

# Handle button presses for subscribe/unsubscribe
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    query.answer()

    # Handle subscription
    if query.data == 'subscribe':
        if chat_id not in subscribed_users:
            subscribed_users.add(chat_id)
            query.edit_message_text(text="You have subscribed to periodic messages!")
        else:
            query.edit_message_text(text="You are already subscribed.")
    
    # Handle unsubscription
    elif query.data == 'unsubscribe':
        if chat_id in subscribed_users:
            subscribed_users.remove(chat_id)
            query.edit_message_text(text="You have unsubscribed from periodic messages.")
        else:
            query.edit_message_text(text="You are not subscribed.")
    elif query.data == 'details':
        mqtt_control.get_detailed_info(_mqtt_context)

            
def telegram_bot_init(mqtt_context):
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Command handler for /start
    dispatcher.add_handler(CommandHandler("start", start))
    # CallbackQueryHandler to handle subscribe/unsubscribe button presses
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Schedule the periodic message
    #schedule.every().hour.do(send_periodic_message)
    
    # Run the scheduler in a background thread
    #def run_schedule():
    #    while True: 
    #        schedule.run_pending()
    #        time.sleep(1)

    # Start the bot and the scheduler
    updater.start_polling()
    #run_schedule()

def main():
    global _mqtt_context
    _mqtt_context = mqtt_control.mqtt_init(send_message)
    telegram_bot_init(_mqtt_context)
    mqtt_control.mqtt_run(_mqtt_context)


if __name__ == '__main__':
    main()
