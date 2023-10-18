from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import PicklePersistence, Application,ConversationHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, CallbackContext
import json
from math import ceil
from typing import Dict
from main import page, total_pages, options
from utils import generate_buttons

async def info_edit(update, context, query):
    keyboard = [
            [
                InlineKeyboardButton("🪙 Coin Details", callback_data="edit_coin"),
                InlineKeyboardButton("💱 Transaction Type", callback_data="edit_type"),
            ],
            [
                InlineKeyboardButton("👀 UI & Apperance", callback_data="edit_ui"),
                InlineKeyboardButton("⚙️ Additional options", callback_data="edit_other"),
            ],
    ]

    reply_text="What category of options would you like to edit?"

    await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def coin_and_address_edit(update, context, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, query=""):
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