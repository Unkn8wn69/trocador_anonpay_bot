import json
import requests
from math import ceil
from typing import Dict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import PicklePersistence, Application,ConversationHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, CallbackContext

def display_if_set(user_info, variable):
    return user_info[variable] if variable in user_info else 'none'

def generate_buttons(options, page, total_pages, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, type):
    start_index = page * COLUMNS_PER_PAGE * OPTIONS_PER_PAGE
    end_index = (page + 1) * COLUMNS_PER_PAGE * OPTIONS_PER_PAGE
    page_options = options[start_index:end_index]

    keyboard = []
    for i in range(0, len(page_options), COLUMNS_PER_PAGE):
        row = []
        for option in page_options[i:i + COLUMNS_PER_PAGE]:
            name = option["name"]
            short_name = option["short"].lower()
            network = option["network"]
            button = InlineKeyboardButton(text=name, callback_data=f"coin_select_{type}_{short_name}_{network}")
            row.append(button)
        keyboard.append(row)

    if page >= 1:
        left_button = InlineKeyboardButton(text="⬅️ Previous", callback_data=f"coin_prev_{type}_{page}")
    else:
        left_button = InlineKeyboardButton(text="🔚 Last", callback_data=f"coin_last_{type}")

    if page + 1 < total_pages:
        right_button = InlineKeyboardButton(text="Next ➡️", callback_data=f"coin_next_{type}_{page}")
    else:
        right_button = InlineKeyboardButton(text="1️⃣ First", callback_data=f"coin_first_{type}")

    page_buttons = [
        left_button,
        InlineKeyboardButton(text=f"📋 {page + 1}/{total_pages}", callback_data=f"coin_prev_{type}{page}"),
        right_button
    ]
    keyboard.append(page_buttons)

    return keyboard

async def validate_address(api_key, ticker, network, address):
    try:
        response = requests.get("https://trocador.app/api/validateaddress", params={"api_key": api_key, "ticker": ticker, "network": network, "address": address})
        if response.status_code == 200:
            data = response.json()
            result = data.get("result")
            return result == True
        else:
            return False

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return False

def generate_link(base_url, params_dict):
    if 'ticker_to' in params_dict and 'network_to' in params_dict and 'address' in params_dict:
        if not base_url:
            raise ValueError("Base URL is required")
        
        if not params_dict:
            return base_url

        exempt_values = {"remove_direct_pay": "False", "simple_mode": "False", "editable": "False"}
        rename_dict = {"direct": "remove_direct_pay", "fiat": "fiat_equiv", "logpolicy": "min_logpolicy", "simple": "simple_mode", "referral": "ref"}

        if rename_dict is not None:
            for old_param, new_param in rename_dict.items():
                if old_param in params_dict:
                    params_dict[new_param] = params_dict.pop(old_param)


        param_list = [f"{key}={value}" for key, value in params_dict.items() if key not in exempt_values or params_dict[key] != exempt_values[key]]
        
        query_string = "&".join(param_list)

        if '?' in base_url:
            return f"{base_url}&{query_string}"
        else:
            return f"{base_url}?{query_string}"
    else:
        return "You have to set a coin and address"