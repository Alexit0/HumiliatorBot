from db import pp_list, mm_list

import logging
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, ReplyKeyboardRemove

from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, \
    CommandHandler, CallbackQueryHandler, ConversationHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

MM_BUTTON = "Ur mama's ass 🚢"
PP_BUTTON = "Ur pp 🔬 "

START_MENU_TEXT = "Hello, I am a humiliation bot. Are you sure you want to continue?"
MENU_TEXT = "You chose to continue. Please choose a subject of humiliation:"
REPEAT_MENU_TEXT = ". \n \n Humiliating enough?"
MENU_TEXT_2 = "Choose the subject then:"

MENU_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton(MM_BUTTON, callback_data="MM"),
                                     InlineKeyboardButton(PP_BUTTON, callback_data="PP")]])

REPEAT_MENU_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton("NO", callback_data='NO'),
                                            InlineKeyboardButton("YES..", callback_data='YES')]])

# States
START_ROUTES, END_ROUTES = range(2)
# Callback data
MENU, CONFIRM_MENU = range(2)

pp_worked = []
mm_worked = []


"""Move random item from the list to depo. 
When the list is empty refill it from depo and empty depo"""


def random_picker(data, new_data):
    if not len(data):
        data = [i for i in new_data]
        new_data = []
    phrase = random.choice(data)
    new_data.append(phrase)
    data.remove(phrase)

    return phrase


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['YES', 'NO']]

    await update.message.reply_text(
        START_MENU_TEXT,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return START_ROUTES


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text=MENU_TEXT, reply_markup=MENU_MARKUP)
    return START_ROUTES


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=MENU_TEXT_2, reply_markup=MENU_MARKUP)
    return START_ROUTES


async def mm_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Your mama's ass is bigger than " +
                                       str(random_picker(mm_list, mm_worked)) + REPEAT_MENU_TEXT,
                                  reply_markup=REPEAT_MENU_MARKUP)
    return END_ROUTES


async def pp_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Your pp is smaller than " +
                                       str(random_picker(pp_list, pp_worked)) + REPEAT_MENU_TEXT,
                                  reply_markup=REPEAT_MENU_MARKUP)
    return END_ROUTES


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Ok, bye then!")
    return ConversationHandler.END


def main():
    application = ApplicationBuilder().token('5978939860:AAH1Rg5hsJ0nnvZof9XIHPHkfrD9JdET0MA').build()

    start_handler = CommandHandler('start', start)
    cancel_handler = CommandHandler(['cancel', 'end'], cancel)

    conv_handler = ConversationHandler(
        entry_points=[start_handler],
        states={
            START_ROUTES: [MessageHandler(filters.Regex("^(YES|NO)$"), menu),
                           CallbackQueryHandler(mm_confirm, pattern="^MM$"),
                           CallbackQueryHandler(pp_confirm, pattern="^PP$")
                           ],
            END_ROUTES: [CallbackQueryHandler(start_over, pattern="NO"),
                         CallbackQueryHandler(end, pattern="YES"),
                         ]
        },
        fallbacks=[cancel_handler]
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
