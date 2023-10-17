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

bot_token = os.environ.get('BOT_TOKEN_TROCADOR')

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

OPTIONS_PER_PAGE = 5
COLUMNS_PER_PAGE = 3

page = 0
total_pages = 0
options = []

def generate_buttons(options, page, page_options):
    start_index = page * COLUMNS_PER_PAGE * OPTIONS_PER_PAGE
    end_index = (page + 1) * COLUMNS_PER_PAGE * OPTIONS_PER_PAGE
    page_options = options[start_index:end_index]

    keyboard = []
    for i in range(0, len(page_options), COLUMNS_PER_PAGE):
        row = []
        for option in page_options[i:i + COLUMNS_PER_PAGE]:
            name = option["name"]
            short_name = option["short"]
            network = option["network"]
            button = InlineKeyboardButton(text=name, callback_data=f"coin_select_{short_name}_{network}")
            row.append(button)
        keyboard.append(row)

    if page > 0:
        prev_button = InlineKeyboardButton(text="Previous Page", callback_data=f"coin_prev_{page}")
        keyboard.append([prev_button])
    if page < total_pages - 1:
        next_button = InlineKeyboardButton(text="Next Page", callback_data=f"coin_next_{page}")
        keyboard.append([next_button])

    return keyboard

async def start(update, context, query=""):
    global page
    global total_pages
    global options
    with open("coins/coins.json", "r") as json_file:
        options = json.load(json_file)
    
    total_pages = int(ceil(len(options) / (COLUMNS_PER_PAGE * OPTIONS_PER_PAGE)))

    keyboard = generate_buttons(options, page, total_pages)

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

            context.user_data['coin'] = selected_coin
            context.user_data['network'] = network

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
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(generate_buttons(options, page, total_pages)))
        elif action == "prev":
            page -= 1
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(generate_buttons(options, page, total_pages)))
        elif action == "edit":
            await update.callback_query.answer()
            await start(update, context, query)
        elif action == "done":
            print("test")
            
async def info(update, context):
    user_info = context.user_data
    
    if user_info:
        info_text = f"Coin: {user_info['coin']}\nNetwork: {user_info['network']}"
        await update.message.reply_text("Your current information:\n" + info_text)
    else:
        await update.message.reply_text("No information available. Use /start to set your information.")

def main() -> None:
    persistence = PicklePersistence(filepath="databot")
    application = Application.builder().token(bot_token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callbacks))
    application.add_handler(CommandHandler('info', info))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
