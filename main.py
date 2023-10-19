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
from edit import *

bot_token = os.environ.get('BOT_TOKEN_TROCADOR')

# logging config
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Variables

GETTING_ADDRESS, GETTING_AMOUNT, GETTING_MEMO, GETTING_NAME, GETTING_DESCRIPTION, GETTING_BUTTONBGCOLOR, GETTING_TEXTCOLOR, GETTING_REFERRAL, GETTING_FIAT, GETTING_EMAIL, GETTING_LOGPOLICY, GETTING_WEBHOOK = range(12)

OPTIONS_PER_PAGE = 5
COLUMNS_PER_PAGE = 3

page = 0
total_pages = 0
options = []


async def coin_and_address_edit(update, context, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, type, query=""):
    global page
    global total_pages
    global options
    with open("coins/coins.json", "r") as json_file:
        options = json.load(json_file)
    
    total_pages = int(ceil(len(options) / (COLUMNS_PER_PAGE * OPTIONS_PER_PAGE)))

    keyboard = generate_buttons(options, page, total_pages, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, type)

    if (type == "coin"):
        reply_text = "Please select a coin:"
    else:
        reply_text = "Please select a coin that should be preselected for the user:"
    try:
        await update.message.reply_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
    except:
        await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start(update, context):
    await coin_and_address_edit(update, context, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, "coin")

async def callbacks(update: Update, context: CallbackContext):
    global page
    global total_pages
    global options
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")

    category = data[0]
    action = data[1]
    user_info = context.user_data

    if category == "coin":
        type = data[2]
        if action == "select":
            selected_coin = data[3]
            network = data[4]

            if (type == "coin"):
                context.user_data['ticker_to'] = selected_coin
                context.user_data['network_to'] = network
            else:
                context.user_data['ticker_from'] = selected_coin
                context.user_data['network_from'] = network

            keyboard = [
            [
                InlineKeyboardButton("Edit", callback_data=f"coin_edit_{type}"),
                InlineKeyboardButton("Next", callback_data=f"coin_done_{type}"),
            ],
            ]

            reply_text = f"You selected the coin: {selected_coin} on {network}"
            await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
        elif action == "next":
            if page < total_pages - 1:
                page += 1
                await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(generate_buttons(options, page, total_pages, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, type)))
        elif action == "prev":
            if page >= 1:
                page -= 1
                await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(generate_buttons(options, page, total_pages, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, type)))
        elif action == "first":
            page = 0
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(generate_buttons(options, page, total_pages, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, type)))
        elif action == "last":
            page = total_pages - 1
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(generate_buttons(options, page, total_pages, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, type)))
        elif action == "edit":
            await update.callback_query.answer()
            await coin_and_address_edit(update, context, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, type)
        elif action == "done":
            if (type == "coin"):
                await query.edit_message_text("Please enter your address:")
                return GETTING_ADDRESS
            else:
                await info(update, context, query)
    elif category == "info":
        if action == "edit":
            await info_edit(update, context, query)
        elif action == "reset":
            await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text="You can reset your data with /reset")
    elif category == "edit":
        if action == "delete":
            var = data[2]
            del user_info[var]
            await info(update, context, query)
        elif action == "coin":
            if len(data) < 3:
                await edit_coin_details(update, context, query, context.user_data)
            else:
                subaction = data[2]
                if subaction == "coin":
                    await coin_and_address_edit(update, context, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, query)
                elif subaction == "amount":
                    await edit_text(update, context, query, user_info, "edit_coin", "What would you like to be the predefined receiving amount? (Example: 0.2)", "amount")
                    return GETTING_AMOUNT
                elif subaction == "memo":
                    await edit_text(update, context, query, user_info, "edit_coin", "What would you like to be the memo/ExtraID for the transaction?","memo")
                    return GETTING_MEMO
        elif action == "type":
            if len(data) < 3:
                await edit_type(update, context, query, context.user_data)
            else:
                subaction = data[2]
                if subaction == "donation":
                    await edit_bool(update, context, query, user_info, subaction, "Would you like this anonpay to be a donation-page?", "edit_type")
                elif subaction == "direct":
                    await edit_bool(update, context, query, user_info, subaction, "When someone wants to pay with your receiving currency over anonpay, would you like that to be disabled?", "edit_type")
                elif subaction == "simple":
                    await edit_bool(update, context, query, user_info, subaction, "Would you like a simpler checkout process? (Better for users that are inexperienced with crypto)", "edit_type")
                elif subaction == "editable":
                    if ("donation" not in user_info or user_info["donation"] != "True"):
                        await edit_bool(update, context, query, user_info, subaction, "Would you like that the user can change the amount?", "edit_type")
                    else:
                        await can_only_edit_when(update, context, query, "You can only change this when Donation is disabled", "❌🫶 Disable Donation", "edit_type", "edit_type_donation")
        elif action == "ui":
            if len(data) < 3:
                await edit_ui(update, context, query, context.user_data)
            else:
                subaction = data[2]
                if subaction == "name":
                    await edit_text(update, context, query, user_info, "edit_ui", "Please send the name you want to appear on the widget. Special characters must be url encoded ( 'A B' is 'A%20B')", "name")
                    return GETTING_NAME
                elif subaction == "description":
                    await edit_text(update, context, query, user_info, "edit_ui", "Please send a description to appear in the checkout screen for the payment/donation. Special characters must be url encoded ( 'A B' is 'A%20B')", "description")
                    return GETTING_DESCRIPTION
                elif subaction == "button":
                    await edit_text(update, context, query, user_info, "edit_ui", "Please send the color of the button, should be in hex format without the '#'. E.g. ff0000 for red. You can get the HEX code from [here](https://www.w3schools.com/colors/colors_picker.asp)", "buttonbgcolor")
                    return GETTING_BUTTONBGCOLOR
                elif subaction == "text":
                    await edit_text(update, context, query, user_info, "edit_ui", "Please send the color of the text, should be in hex format without the '#'. E.g. ff0000 for red. You can get the HEX code from [here](https://www.w3schools.com/colors/colors_picker.asp)", "textcolor")
                    return GETTING_TEXTCOLOR
                elif subaction == "bgcolor":
                    await edit_bool(update, context, query, user_info, "bgcolor", "Do you want to give the page a gray background, otherwise it'll be transparent/white?", "edit_ui")
        elif action == "other":
            if len(data) < 3:
                await edit_other(update, context, query, user_info)
            else:
                subaction = data[2]
                if subaction == "coin":
                    await coin_and_address_edit(update, context, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, "preselected", query)
                elif subaction == "referral":
                    await edit_text(update, context, query, user_info, "edit_other", "Please send your Trocador referral code, if you dont have one get it [here](https://trocador.app/en/affiliate/)", "referral")
                    return GETTING_REFERRAL
                elif subaction == "fiat":
                    await edit_text(update, context, query, user_info, "edit_other", "If you want the amount to be in a fiat equivalent provide a valid currency abbreviation, (example: USD for US-Dollar)", "fiat")
                    return GETTING_FIAT
                elif subaction == "email":
                    await edit_text(update, context, query, user_info, "edit_other", "Enter an email in which you will receive confirmation when the transaction is completed", "email")
                    return GETTING_EMAIL
                elif subaction == "logpolicy":
                    await edit_text(update, context, query, user_info, "edit_other", "If you want to use only on exchanges with a minimum of A, B, C or D log policy rating, please provide this parameter. More info [here](https://trocador.app/en/) under `Is it really private? Isn't KYC required?`", "logpolicy")
                    return GETTING_LOGPOLICY
                elif subaction == "webhook":
                    await edit_text(update, context, query, user_info, "edit_other", "If you provide an URL now, every time the status of the transaction changes, you will receive on this URL a POST request sending you the transaction data; this avoids having to call so many times our server to check the transaction status", "webhook")
                    return GETTING_WEBHOOK
    elif category == "switch":
        await switch_bool(update, context, user_info, data, query)

async def reset_user_data(update, context, query=""):
    user_id = update.effective_user.id
    if len(context.user_data) > 0:
        context.user_data.clear()
        reply_text = "Your user data has been cleared."
        await update.message.reply_text(reply_text)
        await coin_and_address_edit(update, context, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE)
    else:
        reply_text = "No user data found to clear."
        await update.message.reply_text(reply_text)
        await coin_and_address_edit(update, context, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE)

async def switch_bool(update, context, user_info, data, query):
    if data[2] == "no":
        user_info[data[1]] = "False"
        await info(update, context, query)
    else:
        user_info[data[1]] = "True"
        await info(update, context, query)

async def info(update, context, query=""):
    user_info = context.user_data
    
    if user_info:
        info_text = f"""
*Coin Details*

Coin: {display_if_set(user_info, 'ticker_to')}
Network: {display_if_set(user_info, 'network_to')}
Address: `{display_if_set(user_info, 'address')}`
Amount: `{user_info['amount'] if 'amount' in user_info else '0.1'}`
Memo/ExtraID: `{user_info['memo'] if 'memo' in user_info else '0'}`

*Transaction Type*

Donation: {user_info['donation'] if 'donation' in user_info else 'False'}
Remove Direct-Pay: {user_info['direct'] if 'direct' in user_info else 'False'}
Allow to edit amount: {user_info['editable'] if 'editable' in user_info else 'False'}
Simpler checkout: {user_info['simple'] if 'simple' in user_info else 'True'}

*UI & Appearance*

Name: {display_if_set(user_info, 'name')}
Description: {display_if_set(user_info, 'description')}
Button color: `{user_info['buttonbgcolor'] if 'buttonbgcolor' in user_info else 'ff3c00'}`
Text color: `{user_info['textcolor'] if 'textcolor' in user_info else 'fffff'}`
Widget Background: {user_info['bgcolor'] if 'bgcolor' in user_info else 'False'}

*Additional*

Default coin: {user_info['ticker_from'] if 'ticker_from' in user_info else 'BTC'}
Default network: {user_info['network_from'] if 'network_from' in user_info else 'Mainnet'}
Trocador referral: {display_if_set(user_info, 'referral')}
Fiat equivalent: {display_if_set(user_info, 'fiat')}
Notification email: {display_if_set(user_info, 'email')}
Minimum KYC score (A, B or C): {display_if_set(user_info, 'logpolicy')}
Webhook: {display_if_set(user_info, 'webhook')}

*Clearnet Link*: `{generate_link("https://trocador.app/anonpay/", user_info)}`
*Onion Link*: `{generate_link("http://trocadorfyhlu27aefre5u7zri66gudtzdyelymftvr4yjwcxhfaqsid.onion/anonpay/", user_info)}`
"""
        keyboard = [
            [
                InlineKeyboardButton("Edit", callback_data="info_edit"),
                InlineKeyboardButton("Reset", callback_data="info_reset"),
                InlineKeyboardButton("Contribute", url="https://github.com/Unkn8wn69/trocador_anonpay_bot"),
            ],
        ]
        
        try:
            await update.message.reply_text(info_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=info_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("No information available. Use /start to set your information.")

async def get_reply(update, context, var):
    user_data = context.user_data
    user_data[var] = update.message.text

    await info(update, context)
    return ConversationHandler.END

def get_message_handler(var):
    return MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: get_reply(update, context, var))

conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(callbacks)],
    states={
        GETTING_ADDRESS: [get_message_handler("address")],
        GETTING_AMOUNT: [get_message_handler("amount")],
        GETTING_MEMO: [get_message_handler("memo")],
        GETTING_NAME: [get_message_handler("name")],
        GETTING_DESCRIPTION: [get_message_handler("description")],
        GETTING_BUTTONBGCOLOR: [get_message_handler("buttonbgcolor")],
        GETTING_TEXTCOLOR: [get_message_handler("textcolor")],
        GETTING_REFERRAL: [get_message_handler("referral")],
        GETTING_FIAT: [get_message_handler("fiat")],
        GETTING_EMAIL: [get_message_handler("email")],
        GETTING_LOGPOLICY: [get_message_handler("logpolicy")],
        GETTING_WEBHOOK: [get_message_handler("webhook")],
    },
    fallbacks=[],
)

def main() -> None:
    persistence = PicklePersistence(filepath="databot")
    application = Application.builder().token(bot_token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset_user_data))
    application.add_handler(conversation_handler) 
    application.add_handler(CallbackQueryHandler(callbacks))
    application.add_handler(CommandHandler('info', info))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
