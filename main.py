from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler
import random
import time
import qrng
import os
import ast
import logging
import html
import json
import traceback
from dotenv import load_dotenv
# Star Wars Opening Text Amount of imports. :(
    

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
# Set API Keys
bottoken = os.getenv('TELEGRAM_BOT_TOKEN')
ibmtoken = os.getenv('IBMQ_API_KEY')

updater = Updater(token=bottoken, use_context=True)
dispatcher = updater.dispatcher

def error_handler(update: object, context: CallbackContext) -> None:
    # Taken from https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/errorhandlerbot.py
    """Log the error."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)


def roll(update: Update, context: CallbackContext):

    # Gets the input from the /roll command and stores it as a string AND as a list.
    i_string = str(context.args)
    iv_string = context.args

    # Checks to see if there is any input, if there is 3 or more charaters, then we assume that there is.
    if (sum(len(i) for i in iv_string) >= 3):

        # replace D with d
        li_string = str(i_string.replace("D", "d"))

        # Convert it back to a list,
        d_string = ast.literal_eval(li_string)

        dice = int(d_string[0].partition("d")[0]) + 1
        sides = int(d_string[0].partition("d")[2]) + 1
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Getting A Seed Value From IBM's Quantum Computer")
        time.sleep(0.5)
        seed_string = qrng.get_random_int32()
        random.seed(seed_string)
        context.bot.send_message(chat_id=update.effective_chat.id, text="The random seed is: " + str(seed_string) + "! "
                                 "Starting "
                                 "the roll!")
        # print("Number of dice" + dice)
        # print("Number of sides" + sides)
        for die in range(1, dice):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=str(("Die Number" + str(die) + ":" + str(random.randrange(1, int(sides))))))
            time.sleep(0.5)
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Done!")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Invaild Input, make sure it is in the format of **x**d**y** \n Where **x** is the number of dice and **y** is the number of sides\. \n E\.G\. to roll 3 dice with 8 sides each\. 3d8\.", parse_mode=ParseMode.MARKDOWN_V2)
    # print(i_string)


qrng.set_provider_as_IBMQ(ibmtoken)
qrng.set_backend('ibmq_bogota')
roll_handler = CommandHandler('roll', roll)
dispatcher.add_handler(roll_handler)
dispatcher.add_error_handler(error_handler)
updater.start_polling()
