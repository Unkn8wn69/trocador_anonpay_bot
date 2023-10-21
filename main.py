#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

import logging
import json
from dotenv import load_dotenv
from math import ceil
from typing import Dict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, constants
from telegram.ext import PicklePersistence, Application,ConversationHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, CallbackContext
import os
import re
from utils import *
from edit import *
from strings import *

load_dotenv()
bot_token = os.getenv('BOT_TOKEN_TROCADOR')
api_key = os.getenv('API_KEY')

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


async def coin_and_address_edit(update, context, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, type, query=None):
    global page
    global total_pages
    global options
    page = 0
    with open("coins/coins.json", "r") as json_file:
        options = json.load(json_file)
    
    total_pages = int(ceil(len(options) / (COLUMNS_PER_PAGE * OPTIONS_PER_PAGE)))

    keyboard = generate_buttons(options, page, total_pages, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, type)

    if (type == "coin"):
        reply_text = replies['select_receving']
    else:
        reply_text = replies['select_preselected']
    
    await send_formatted_message(update, context, reply_text, keyboard, query)

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
            await coin_and_address_edit(update, context, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, type, query)
        elif action == "done":
            if (type == "coin"):
                await query.edit_message_text("Please enter your receiving address:")
                return GETTING_ADDRESS
            else:
                await info(update, context, query)
    elif category == "info":
        if action == "edit":
            await info_edit(update, context, query)
        elif action == "reset":
            await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text="You can reset your data with /reset")
        elif action == "show":
            await info(update, context, query)
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
                    await edit_text(update, context, query, user_info, '_'.join(data[:2]), editing_questions[subaction], data[2])
                    return GETTING_AMOUNT
                elif subaction == "memo":
                    await edit_text(update, context, query, user_info, '_'.join(data[:2]), editing_questions[subaction], data[2])
                    return GETTING_MEMO
        elif action == "type":
            if len(data) < 3:
                await edit_type(update, context, query, context.user_data)
            else:
                subaction = data[2]
                if subaction == "donation":
                    await edit_bool(update, context, query, user_info, subaction, editing_questions[subaction], '_'.join(data[:2]))
                elif subaction == "direct":
                    await edit_bool(update, context, query, user_info, subaction, editing_questions[subaction], '_'.join(data[:2]))
                elif subaction == "simple":
                    await edit_bool(update, context, query, user_info, subaction, editing_questions[subaction], '_'.join(data[:2]))
                elif subaction == "editable":
                    if ("donation" not in user_info or user_info["donation"] != "True"):
                       await edit_bool(update, context, query, user_info, subaction, editing_questions[subaction], '_'.join(data[:2]))
                    else:
                        await can_only_edit_when(update, context, query, editing_questions["cant_donation"], "❌🫶 Disable Donation", "edit_type", "edit_type_donation")
        elif action == "ui":
            if len(data) < 3:
                await edit_ui(update, context, query, context.user_data)
            else:
                subaction = data[2]
                if subaction == "name":
                    await edit_text(update, context, query, user_info, '_'.join(data[:2]), editing_questions[subaction], data[2])
                    return GETTING_NAME
                elif subaction == "description":
                    await edit_text(update, context, query, user_info, '_'.join(data[:2]), editing_questions[subaction], data[2])
                    return GETTING_DESCRIPTION
                elif subaction == "buttonbgcolor":
                    await edit_text(update, context, query, user_info, '_'.join(data[:2]), editing_questions[subaction], data[2])
                    return GETTING_BUTTONBGCOLOR
                elif subaction == "textcolor":
                    await edit_text(update, context, query, user_info, '_'.join(data[:2]), editing_questions[subaction], data[2])
                    return GETTING_TEXTCOLOR
                elif subaction == "bgcolor":
                    await edit_bool(update, context, query, user_info, subaction, editing_questions[subaction], '_'.join(data[:2]))
        elif action == "other":
            if len(data) < 3:
                await edit_other(update, context, query, user_info)
            else:
                subaction = data[2]
                if subaction == "coin":
                    await coin_and_address_edit(update, context, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, "preselected", query)
                elif subaction == "referral":
                    await edit_text(update, context, query, user_info, '_'.join(data[:2]), editing_questions[subaction], data[2])
                    return GETTING_REFERRAL
                elif subaction == "fiat":
                    await edit_text(update, context, query, user_info, '_'.join(data[:2]), editing_questions[subaction], data[2])
                    return GETTING_FIAT
                elif subaction == "email":
                    await edit_text(update, context, query, user_info, '_'.join(data[:2]), editing_questions[subaction], data[2])
                    return GETTING_EMAIL
                elif subaction == "logpolicy":
                    await edit_text(update, context, query, user_info, '_'.join(data[:2]), editing_questions[subaction], data[2])
                    return GETTING_LOGPOLICY
                elif subaction == "webhook":
                    await edit_text(update, context, query, user_info, '_'.join(data[:2]), editing_questions[subaction], data[2])
                    return GETTING_WEBHOOK
    elif category == "switch":
        await switch_bool(update, context, user_info, data, query)

async def reset_user_data(update, context, query=None):
    user_id = update.effective_user.id
    if len(context.user_data) > 0:
        context.user_data.clear()
        reply_text = "Your user data has been cleared."
        await update.message.reply_text(reply_text)
        await coin_and_address_edit(update, context, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, "coin")
    else:
        reply_text = "No user data found to clear."
        await update.message.reply_text(reply_text)
        await coin_and_address_edit(update, context, OPTIONS_PER_PAGE, COLUMNS_PER_PAGE, "coin")

async def switch_bool(update, context, user_info, data, query):
    if data[2] == "no":
        user_info[data[1]] = "False"
        await info(update, context, query)
    else:
        user_info[data[1]] = "True"
        await info(update, context, query)

async def info(update, context, query=None):
    user_info = context.user_data
    
    if user_info:
        info_text = f"""
{text_coin_details(user_info)}

{text_transaction_type(user_info)}

{text_ui(user_info)}

{text_other(user_info)}

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
        
        await send_formatted_message(update, context, info_text, keyboard, query)
    else:
        reply_text = replies['info_coin_address_not_set']
        await send_formatted_message(update, context, reply_text, keyboard, query)

async def get_reply(update, context, var):
    user_data = context.user_data
    user_data[var] = update.message.text

    await info(update, context)
    return ConversationHandler.END

async def get_address(update, context):
    user_data = context.user_data
    await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=constants.ChatAction.TYPING)

    if (await validate_address(api_key, user_data['ticker_to'], user_data['network_to'], update.message.text)):
        user_data['address'] = update.message.text
        await info(update, context)
        return ConversationHandler.END
    else:
        keyboard = [
            [
                InlineKeyboardButton("⬅️ back", callback_data="coin_edit_coin"),
            ],
        ]

        await update.message.reply_text("The entered address is not valid. Please enter your address again:", reply_markup=InlineKeyboardMarkup(keyboard))
        return GETTING_ADDRESS

async def get_valid_answer(update, context, var, regex, callback, back_callback, text):
    user_data = context.user_data
    reply = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=constants.ChatAction.TYPING)

    if re.match(regex, reply):
        user_data[var] = reply
        await info(update, context)
        return ConversationHandler.END
    else:
        await edit_text(update, context, None, user_data, back_callback, text, var)
        return callback
        
def get_message_handler(var):
    return MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: get_reply(update, context, var))

def get_validated_message_handler(var, return_value, callback, regex):
    return MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: get_valid_answer(update, context, var, regex, return_value, callback, editing_questions[var]))

conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(callbacks)],
    states={
        GETTING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: get_address(update, context))],
        GETTING_AMOUNT: [get_validated_message_handler("amount", GETTING_AMOUNT, "edit_coin", r'^\d+(\.\d+)?$')],
        GETTING_MEMO: [get_message_handler("memo")],
        GETTING_NAME: [get_message_handler("name")],
        GETTING_DESCRIPTION: [get_message_handler("description")],
        GETTING_BUTTONBGCOLOR: [get_validated_message_handler("buttonbgcolor", GETTING_BUTTONBGCOLOR, "edit_ui", r'\b[0-9A-Fa-f]{6}\b')],
        GETTING_TEXTCOLOR: [get_validated_message_handler("textcolor", GETTING_TEXTCOLOR, "edit_ui", r'\b[0-9A-Fa-f]{6}\b')],
        GETTING_REFERRAL: [get_message_handler("referral")],
        GETTING_FIAT: [get_validated_message_handler("fiat", GETTING_FIAT, "edit_other", r'\b(?:' + '|'.join(map(re.escape, available_currencies)) + r')\b')],
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
