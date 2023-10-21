from utils import display_if_set

def text_coin_details(user_info):
    return f"""🪙 *Coin Details*

🪙 Coin: {display_if_set(user_info, 'ticker_to')}
🌐 Network: {display_if_set(user_info, 'network_to')}
📩 Address: `{display_if_set(user_info, 'address')}`
🫰 Amount: `{user_info['amount'] if 'amount' in user_info else '0.1'}`
🆔 Memo/ExtraID: `{user_info['memo'] if 'memo' in user_info else '0'}`"""

def text_transaction_type(user_info):
    return f"""
💱 *Transaction Type*

🫶 Donation: {user_info['donation'] if 'donation' in user_info else 'False'}
❌🎯 Remove Direct-Pay: {user_info['direct'] if 'direct' in user_info else 'False'}
⚖️ Allow to edit amount: {user_info['editable'] if 'editable' in user_info else 'False'}
👌 Simpler checkout: {user_info['simple'] if 'simple' in user_info else 'True'}"""

def text_ui(user_info):
    return f"""
👀 *UI & Appearance*

📛 Name: {display_if_set(user_info, 'name')}
🔤 Description: {display_if_set(user_info, 'description')}
🔳🎨 Button color: `{user_info['buttonbgcolor'] if 'buttonbgcolor' in user_info else 'ff3c00'}`
🔤🎨 Text color: `{user_info['textcolor'] if 'textcolor' in user_info else 'fffff'}`
🔲 Widget Background: {user_info['bgcolor'] if 'bgcolor' in user_info else 'False'}"""

def text_other(user_info):
    return f"""
⚙️ *Additional*

🪙 Default coin: {user_info['ticker_from'] if 'ticker_from' in user_info else 'BTC'}
🌐 Default network: {user_info['network_from'] if 'network_from' in user_info else 'Mainnet'}
🤝 Trocador referral: {display_if_set(user_info, 'referral')}
💲 Fiat equivalent: {display_if_set(user_info, 'fiat')}
📧 Notification email: {display_if_set(user_info, 'email')}
🥇 Minimum KYC score (A, B or C): {display_if_set(user_info, 'logpolicy')}
🌐 Webhook: {display_if_set(user_info, 'webhook')}"""

replies = {
    "select_receving": "Please select the coin you want to receive:",
    "select_preselected": "Please select a coin that should be preselected for the user:",
    "info_coin_address_not_set": "Receiving coin and address not set, please set it with /start",

}

editing_questions = {
    "amount": "What would you like to be the predefined receiving amount? (Example: 0.2)",
    "memo": "What would you like to be the memo/ExtraID for the transaction?",
    "donation": "Would you like this anonpay to be a donation-page?",
    "cant_donation": "You can only change this when Donation is disabled",
    "direct": "When someone wants to pay with your receiving currency over anonpay, would you like that to be disabled?",
    "simple": "Would you like a simpler checkout process? (Better for users that are inexperienced with crypto)",
    "editable": "Would you like that the user can change the amount?",
    "name": "Please send the name you want to appear on the widget. Special characters must be url encoded ('A B' is 'A%20B')",
    "description": "Please send a description to appear in the checkout screen for the payment/donation. Special characters must be url encoded ('A B' is 'A%20B')",
    "buttonbgcolor": "Please send the color of the button, should be in hex format without the '#' (e.g., ff0000 for red). You can get the HEX code from [here](https://www.w3schools.com/colors/colors_picker.asp)",
    "textcolor": "Please send the color of the text, should be in hex format without the '#' (e.g., ff0000 for red). You can get the HEX code from [here](https://www.w3schools.com/colors/colors_picker.asp)",
    "bgcolor": "Do you want to give the page a gray background, otherwise it'll be transparent/white?",
    "coin": "Please specify the coin and address details.",
    "referral": "Please send your Trocador referral code, if you don't have one, get it [here](https://trocador.app/en/affiliate/)",
    "fiat": "If you want the amount to be in a fiat equivalent, provide a valid currency abbreviation (example: USD for US-Dollar).",
    "email": "Enter an email in which you will receive confirmation when the transaction is completed",
    "logpolicy": "If you want to use only on exchanges with a minimum of A, B, C, or D log policy rating, please provide this parameter. More info [here](https://trocador.app/en/) under 'Is it really private? Isn't KYC required?'",
    "webhook": "If you provide a URL now, every time the status of the transaction changes, you will receive on this URL a POST request sending you the transaction data; this avoids having to call our server multiple times to check the transaction status."
}

available_currencies = ['USD','EUR', 'AED',	'AFN',	'ALL',	'AMD',	'ANG',	'AOA',	'ARS',	'AUD',	'AWG',	'AZN',	'BAM',	'BBD',	'BDT',	'BGN',	'BHD',	'BIF',	'BMD',	'BND',	'BOB',	'BOV',	'BRL',	'BSD',	'BTN',	'BWP',	'BYN',	'BZD',	'CAD',	'CDF',	'CHE',	'CHF',	'CHW',	'CLF',	'CLP',	'COP',	'COU',	'CRC',	'CUC',	'CUP',	'CVE',	'CZK',	'DJF',	'DKK',	'DOP',	'DZD',	'EGP',	'ERN',	'ETB',	'FJD',	'FKP',	'GBP',	'GEL',	'GHS',	'GIP',	'GMD',	'GNF',	'GTQ',	'GYD',	'HKD',	'HNL',	'HTG',	'HUF',	'IDR',	'ILS',	'INR',	'IQD',	'IRR',	'ISK',	'JMD',	'JOD',	'JPY',	'KES',	'KGS',	'KHR',	'KMF',	'KPW',	'KRW',	'KWD',	'KYD',	'KZT',	'LAK',	'LBP',	'LKR',	'LRD',	'LSL',	'LYD',	'MAD',	'MDL',	'MGA',	'MKD',	'MMK',	'MNT',	'MOP',	'MRU',	'MUR',	'MVR',	'MWK',	'MXN',	'MXV',	'MYR',	'MZN',	'NAD',	'NGN',	'NIO',	'NOK',	'NPR',	'NZD',	'OMR',	'PAB',	'PEN',	'PGK',	'PHP',	'PKR',	'PLN',	'PYG',	'QAR',	'RON',	'RSD',	'CNY',	'RUB',	'RWF',	'SAR',	'SBD',	'SCR',	'SDG',	'SEK',	'SGD',	'SHP',	'SLE',	'SLL',	'SOS',	'SRD',	'SSP',	'STN',	'SVC',	'SYP',	'SZL',	'THB',	'TJS',	'TMT',	'TND',	'TOP',	'TRY',	'TTD',	'TWD',	'TZS',	'UAH',	'UGX',	'USN',	'UYI',	'UYU',	'UYW',	'UZS',	'VED',	'VES',	'VND',	'VUV',	'WST',	'XAF',	'XAG',	'XAU',	'XBA',	'XBB',	'XBC',	'XBD',	'XCD',	'XDR',	'XOF',	'XPD',	'XPF',	'XPT',	'XSU',	'XTS',	'XUA',	'XXX',	'YER',	'ZAR',	'ZMW',	'ZWL']
