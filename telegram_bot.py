import time
#import schedule
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, Application, ContextTypes

import mqtt_control
import sweet_home_controller

import gettext
import locale
import logging
import asyncio

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Choose language dynamically or set by locale
lang = gettext.translation('telegram_bot', localedir='locale', languages=['ua'])
lang.install()
_ = lang.gettext

def send_message(bot,  msg):
    print(msg)
    async def send_msg(bot, chat, msg):
        await bot.send_message(chat_id=chat, text=msg)
    for chat_id in sweet_home_controller.telegram_get_subsribed_users():
        asyncio.run_coroutine_threadsafe(send_msg(bot["bot"], chat_id, msg), bot["loop"])

def send_html_message(bot,  msg):
    print(msg)
    async def send_msg(bot, chat, msg):
        await bot.send_message(chat_id=chat, text=msg, parse_mode=ParseMode.HTML)

    for chat_id in sweet_home_controller.telegram_get_subsribed_users():
        asyncio.run_coroutine_threadsafe(send_msg(bot["bot"], chat_id, msg), bot["loop"])

MAIN_MENU = [
    [InlineKeyboardButton(_("Status"), callback_data='status')],
    [InlineKeyboardButton(_("Config"), callback_data='config')],
    [InlineKeyboardButton(_("Debug"), callback_data='debug')],
]
# Start command handler to display the subscription menu
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    print("Request start from user {}".format(chat_id))
    if sweet_home_controller.telegram_is_user_allowed(chat_id):
        keyboard = MAIN_MENU
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send the menu
        await context.bot.send_message(chat_id=chat_id, text=_("Sweet home bot"), reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=chat_id, text="Access denied")

# Handle button presses
async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    query.answer()
    print("Request button from user {}".format(chat_id))
    # Handle subscription
    if not sweet_home_controller.telegram_is_user_allowed(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="Access denied")
        return

    if query.data == 'config':
        keyboard = [
            [InlineKeyboardButton(_("Subscribe"), callback_data='subscribe')],
            [InlineKeyboardButton(_("Unsubscribe"), callback_data='unsubscribe')],
            [InlineKeyboardButton(_("Main menu"), callback_data='main menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send the menu
        #context.bot.send_message(chat_id=chat_id, text="Change an configuration:", reply_markup=reply_markup)
        await query.edit_message_text(text=_("Change an configuration:"), reply_markup=reply_markup)
    elif query.data == 'status':
        keyboard = [
            [InlineKeyboardButton(_("Detailed"), callback_data='detailed status')],
            [InlineKeyboardButton(_("Statistic"), callback_data='statistic')],
            [InlineKeyboardButton(_("Main menu"), callback_data='main menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send the menu
        #context.bot.send_message(chat_id=chat_id, text="Change an configuration:", reply_markup=reply_markup)
        text = sweet_home_controller.devices_get_last_messages()
        print(text)
        if text == '':
            text = "No data"
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    elif query.data == 'statistic':
        keyboard = [
            [InlineKeyboardButton(_("daily"), callback_data='statistic 1 day')],
            [InlineKeyboardButton(_("weekly"), callback_data='statistic 7 day')],
            [InlineKeyboardButton(_("Main menu"), callback_data='main menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send the menu
        await query.edit_message_text(text=_("Statistic period"), reply_markup=reply_markup)
    elif query.data == 'statistic 1 day':
        keyboard = [
            [InlineKeyboardButton(_("Main menu"), callback_data='main menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        images = sweet_home_controller.devices_get_statistic_graph(1)
        await query.edit_message_text(text=_("1 day statistic"), reply_markup=reply_markup)
        for i in images:
            await context.bot.send_photo(chat_id=chat_id, photo=i, caption=_("Here's your daily statistics graph!"))
            i.close()
    elif query.data == 'statistic 7 day':
        keyboard = [
            [InlineKeyboardButton(_("Main menu"), callback_data='main menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        images = sweet_home_controller.devices_get_statistic_graph(7)
        await query.edit_message_text(text=_("Week statistic"), reply_markup=reply_markup)
        for i in images:
            await context.bot.send_photo(chat_id=chat_id, photo=i, caption=_("Here's your weekly statistics graph!"))
            i.close()
    elif query.data == 'detailed status':
        keyboard = [
            [InlineKeyboardButton(_("Main menu"), callback_data='main menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = sweet_home_controller.devices_get_last_messages(False)
        await query.edit_message_text(text=text, reply_markup=reply_markup)
    elif query.data == 'subscribe':
        keyboard = [
            [InlineKeyboardButton(_("Main menu"), callback_data='main menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if not sweet_home_controller.telegram_is_user_subsribed(chat_id):
            sweet_home_controller.telegram_set_user_subsribed(chat_id, True)
            await query.edit_message_text(text=_("You have subscribed to messages!"), reply_markup=reply_markup)
        else:
            await query.edit_message_text(text=_("You are already subscribed."), reply_markup=reply_markup)

    # Handle unsubscription
    elif query.data == 'unsubscribe':
        keyboard = [
            [InlineKeyboardButton(_("Main menu"), callback_data='main menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if sweet_home_controller.telegram_is_user_subsribed(chat_id):
            sweet_home_controller.telegram_set_user_subsribed(chat_id, False)
            await query.edit_message_text(text=_("You have unsubscribed from messages."), reply_markup=reply_markup)
        else:
            await query.edit_message_text(text=_("You are not subscribed."), reply_markup=reply_markup)
    elif query.data == 'main menu':
        keyboard = MAIN_MENU
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=_("Sweet home bot"), reply_markup=reply_markup)



def telegram_bot_init(bot_token):
    loop = asyncio.get_event_loop()
    bot = Bot(token=bot_token)
    return {"bot":bot,
            "loop":loop}

def telegram_bot_start(bot_token):
    # try:
    #     updater = Updater(token=bot_token, use_context=True, request_kwargs={'read_timeout': 20, 'connect_timeout': 20})
    #     dispatcher = updater.dispatcher

    #     # Command handler for /start
    #     dispatcher.add_handler(CommandHandler("start", start))
    #     # CallbackQueryHandler to handle subscribe/unsubscribe button presses
    #     dispatcher.add_handler(CallbackQueryHandler(button))

    #     # Schedule the periodic message
    #     #schedule.every().hour.do(send_periodic_message)

    #     # Run the scheduler in a background thread
    #     #def run_schedule():
    #     #    while True:
    #     #        schedule.run_pending()
    #     #        time.sleep(1)

    #     # Start the bot and the scheduler
    #     updater.start_polling()
    # except Exception as e:
    #     logging.exception("An error occurred while starting the bot.")
    # #run_schedule()

    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    _mqtt_context = mqtt_control.mqtt_init(send_message)
    telegram_bot_init(_mqtt_context)
    mqtt_control.mqtt_run(_mqtt_context)


if __name__ == '__main__':
    main()
