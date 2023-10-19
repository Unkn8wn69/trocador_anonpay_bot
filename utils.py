import json
from math import ceil
from typing import Dict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import PicklePersistence, Application,ConversationHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, CallbackContext

def display_if_set(user_info, variable):
    return user_info[variable] if variable in user_info else 'none'

def generate_buttons(options, page, total_pages, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE):
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

    if page >= 1:
        left_button = InlineKeyboardButton(text="⬅️ Previous", callback_data=f"coin_prev_{page}")
    else:
        left_button = InlineKeyboardButton(text="🔚 Last", callback_data=f"coin_last")

    if page + 1 < total_pages:
        right_button = InlineKeyboardButton(text="Next ➡️", callback_data=f"coin_next_{page}")
    else:
        right_button = InlineKeyboardButton(text="1️⃣ First", callback_data=f"coin_first")

    page_buttons = [
        left_button,
        InlineKeyboardButton(text=f"📋 {page + 1}/{total_pages}", callback_data=f"coin_prev_{page}"),
        right_button
    ]
    keyboard.append(page_buttons)

    return keyboard

def generate_link(user_info):
    if 'ticker_to' in user_info and 'network_to' in user_info and 'address' in user_info:
        return f"https://trocador.app/anonpay/?ticker_to={user_info['ticker_to']}&network_to={user_info['network_to']}&address={user_info['address']}"
    else:
        return "You have to set a coin and address"