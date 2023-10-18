#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

import logging
import json
from math import ceil
from typing import Dict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import PicklePersistence, Application,ConversationHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, CallbackContext
import os
from utils import *

bot_token = os.environ.get('BOT_TOKEN_TROCADOR')

# logging config
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Variables

GETTING_ADDRESS = range(1)

OPTIONS_PER_PAGE = 5
COLUMNS_PER_PAGE = 3

page = 0
total_pages = 0
options = []

async def start(update, context, query=""):
    global page
    global total_pages
    global options
    with open("coins/coins.json", "r") as json_file:
        options = json.load(json_file)
    
    total_pages = int(ceil(len(options) / (COLUMNS_PER_PAGE * OPTIONS_PER_PAGE)))

    keyboard = generate_buttons(options, page, total_pages, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE)

    reply_text = "Please select a coin:"
    try:
        await update.message.reply_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
    except:
        await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def callbacks(update: Update, context: CallbackContext):
    global page
    global total_pages
    global options
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")

    category = data[0]

    if category == "coin":
        action = data[1]
        if action == "select":
            selected_coin = data[2]
            network = data[3]

            context.user_data['ticker_to'] = selected_coin
            context.user_data['network_to'] = network

            keyboard = [
            [
                InlineKeyboardButton("Edit", callback_data="coin_edit"),
                InlineKeyboardButton("Next", callback_data="coin_done"),
            ],
            ]

            reply_text = f"You selected the coin: {selected_coin} on {network}"
            await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
        elif action == "next":
            page += 1
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(generate_buttons(options, page, total_pages, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE)))
        elif action == "prev":
            page -= 1
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(generate_buttons(options, page, total_pages, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE)))
        elif action == "edit":
            await update.callback_query.answer()
            await start(update, context, query)
        elif action == "done":
            await query.edit_message_text("Please enter your address:")
            return GETTING_ADDRESS

async def get_address(update, context):
    user_data = context.user_data
    user_data['address'] = update.message.text

    await update.message.reply_text("Address saved. You can now continue.")
    return ConversationHandler.END

async def info(update, context):
    user_info = context.user_data
    
    if user_info:
        info_text = f"""
Coin: {display_if_set(user_info, 'ticker_to')}
Network: {display_if_set(user_info, 'network_to')}
Address: `{display_if_set(user_info, 'address')}`

*Design options:*

Button color: `{user_info['buttonbgcolor'] if 'buttonbgcolor' in user_info else 'ff3c00'}`
Text color: `{user_info['textcolor'] if 'textcolor' in user_info else 'fffff'}`
Widget Background: {user_info['bgcolor'] if 'bgcolor' in user_info else 'False'}

Link: `{generate_link(user_info)}`
"""
        #info_text = f"Coin: {user_info['ticker_to']}\nNetwork: {user_info['network_to']}\nAddress: {user_info['address']}"
        await update.message.reply_text("*Your current options:*\n" + info_text, parse_mode='Markdown')
    else:
        await update.message.reply_text("No information available. Use /start to set your information.")

address_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)

address_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(callbacks)],
    states={
        GETTING_ADDRESS: [address_handler],
    },
    fallbacks=[],
)

def main() -> None:
    persistence = PicklePersistence(filepath="databot")
    application = Application.builder().token(bot_token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(address_conversation_handler) 
    application.add_handler(CallbackQueryHandler(callbacks))
    application.add_handler(CommandHandler('info', info))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
