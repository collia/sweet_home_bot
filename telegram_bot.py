import time
#import schedule
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import mqtt_control
import sweet_home_controller

import gettext
import locale

# Choose language dynamically or set by locale
lang = gettext.translation('telegram_bot', localedir='locale', languages=['ua'])
lang.install()
_ = lang.gettext

def send_message(bot, msg):
    print(msg)
    for chat_id in sweet_home_controller.telegram_get_subsribed_users():
        bot.send_message(chat_id=chat_id, text=msg)

# Start command handler to display the subscription menu
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    print("Request start from user {}".format(chat_id))
    if sweet_home_controller.telegram_is_user_allowed(chat_id):
        keyboard = [
            [InlineKeyboardButton(_("Status"), callback_data='status')],
            [InlineKeyboardButton(_("Config"), callback_data='config')],
            [InlineKeyboardButton(_("Debug"), callback_data='debug')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send the menu
        context.bot.send_message(chat_id=chat_id, text=_("Sweet home bot"), reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=chat_id, text="Access denied")

# Handle button presses for subscribe/unsubscribe
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    query.answer()
    print("Request button from user {}".format(chat_id))
    # Handle subscription
    if not sweet_home_controller.telegram_is_user_allowed(chat_id):
        context.bot.send_message(chat_id=chat_id, text="Access denied")
        return
        
    if query.data == 'config':
        keyboard = [
            [InlineKeyboardButton(_("Subscribe"), callback_data='subscribe')],
            [InlineKeyboardButton(_("Unsubscribe"), callback_data='unsubscribe')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send the menu
        #context.bot.send_message(chat_id=chat_id, text="Change an configuration:", reply_markup=reply_markup)
        query.edit_message_text(text=_("Change an configuration:"), reply_markup=reply_markup)
    elif query.data == 'status':
        keyboard = [
            [InlineKeyboardButton(_("Detailed"), callback_data='detailed status')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send the menu
        #context.bot.send_message(chat_id=chat_id, text="Change an configuration:", reply_markup=reply_markup)
        text = sweet_home_controller.devices_get_last_messages()
        query.edit_message_text(text=text, reply_markup=reply_markup)
    elif query.data == 'detailed status':
        text = sweet_home_controller.devices_get_last_messages(False)
        query.edit_message_text(text=text)

    elif query.data == 'subscribe':
        if not sweet_home_controller.telegram_is_user_subsribed(chat_id):
            sweet_home_controller.telegram_set_user_subsribed(chat_id, True)
            query.edit_message_text(text=_("You have subscribed to messages!"))
        else:
            query.edit_message_text(text=_("You are already subscribed."))
    
    # Handle unsubscription
    elif query.data == 'unsubscribe':
        if sweet_home_controller.telegram_is_user_subsribed(chat_id):
            sweet_home_controller.telegram_set_user_subsribed(chat_id, False)
            query.edit_message_text(text=_("You have unsubscribed from messages."))
        else:
            query.edit_message_text(text=_("You are not subscribed."))
            
def telegram_bot_init(bot_token, mqtt_context):
    bot = Bot(token=bot_token)
    updater = Updater(token=bot_token, use_context=True)
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
    return bot

def main():
    _mqtt_context = mqtt_control.mqtt_init(send_message)
    telegram_bot_init(_mqtt_context)
    mqtt_control.mqtt_run(_mqtt_context)


if __name__ == '__main__':
    main()
