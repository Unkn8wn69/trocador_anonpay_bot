from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import PicklePersistence, Application,ConversationHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, CallbackContext
import json
from math import ceil
from typing import Dict
from main import page, total_pages, options
from utils import generate_buttons, display_if_set
from strings import *

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
            [
                InlineKeyboardButton("⬅️ Back", callback_data="info_show"),
            ]
    ]

    reply_text="What category of options would you like to edit?"

    await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def edit_bool(update, context, query, user_info, variable, text, back_callback):
    keyboard = [
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"switch_{variable}_yes"),
                InlineKeyboardButton("❌ No", callback_data=f"switch_{variable}_no"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data=back_callback),
            ],
    ]

    reply_text=text

    await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=reply_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def edit_text(update, context, query, user_info, back_callback, text, var):
    keyboard = [
            [
                InlineKeyboardButton("❌ Cancel", callback_data=back_callback),
                InlineKeyboardButton("🗑️ Delete", callback_data=f"edit_delete_{var}")
            ],
    ]

    try:
        await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    except:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def can_only_edit_when(update, context, query, text, text_edit, back_callback, edit_callback):
    keyboard = [
            [
                InlineKeyboardButton("🆗 Okay", callback_data=back_callback),
                InlineKeyboardButton(text_edit, callback_data=edit_callback)
            ],
    ]

    await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


# Editing questions for coin details

async def edit_coin_details(update, context, query, user_info):
    keyboard = [
            [
                InlineKeyboardButton("⬅️ Back", callback_data="info_edit"),
                InlineKeyboardButton("🪙 Crypto & Address", callback_data="edit_coin_coin"),
            ],
            [
                InlineKeyboardButton("🫰 Amount", callback_data="edit_coin_amount"),
                InlineKeyboardButton("🆔 Memo/ExtraID", callback_data="edit_coin_memo"),
            ],
    ]

    reply_text=f"""
{text_coin_details(user_info)}

*What option would you like to edit?*
"""

    await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=reply_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# Editing the Transaction type

async def edit_type(update, context, query, user_info):
    keyboard = [
            [
                InlineKeyboardButton("⬅️ Back", callback_data="info_edit"),
                InlineKeyboardButton("🫶 Donation", callback_data="edit_type_donation"),
                InlineKeyboardButton("🎯 Direct-Pay", callback_data="edit_type_direct"),
            ],
            [
                InlineKeyboardButton("👌 Simple checkout", callback_data="edit_type_simple"),
                InlineKeyboardButton("⚖️ Editable Amount", callback_data="edit_type_editable"),
            ],
    ]

    reply_text=f"""
{text_transaction_type(user_info)}

*What option would you like to edit?*
"""

    await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=reply_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# Editing the UI & Apperance

async def edit_ui(update, context, query, user_info):
    keyboard = [
            [
                InlineKeyboardButton("⬅️ Back", callback_data="info_edit"),
                InlineKeyboardButton("📛 Name", callback_data="edit_ui_name"),
                InlineKeyboardButton("🔣 Description", callback_data="edit_ui_description"),
            ],
            [
                InlineKeyboardButton("🔳 Button", callback_data="edit_ui_buttonbgcolor"),
                InlineKeyboardButton("🔤 Text", callback_data="edit_ui_textcolor"),
                InlineKeyboardButton("🔲 Background", callback_data="edit_ui_bgcolor"),
            ],
    ]

    reply_text=f"""
{text_ui(user_info)}

*What option would you like to edit?*
"""

    await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=reply_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

## Additional options

async def edit_other(update, context, query, user_info):
    keyboard = [
            [
                InlineKeyboardButton("⬅️ Back", callback_data="info_edit"),
                InlineKeyboardButton("🪙 Preselected", callback_data="edit_other_coin"),
                InlineKeyboardButton("🤝 Referral", callback_data="edit_other_referral"),
            ],
            [
                InlineKeyboardButton("💲 Fiat equivalent", callback_data="edit_other_fiat"),
                InlineKeyboardButton("📧 Notification Email", callback_data="edit_other_email"),
            ],
            [
                InlineKeyboardButton("🥇 Minimum KYC-Score", callback_data="edit_other_logpolicy"),
                InlineKeyboardButton("🌐 Webhook", callback_data="edit_other_webhook"),
            ],
    ]

    reply_text=f"""
{text_other(user_info)}

*What option would you like to edit?*
"""

    await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,text=reply_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))