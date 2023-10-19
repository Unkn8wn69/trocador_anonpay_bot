from utils import display_if_set

def text_coin_details(user_info):
    return f"""*Coin Details*

Coin: {display_if_set(user_info, 'ticker_to')}
Network: {display_if_set(user_info, 'network_to')}
Address: `{display_if_set(user_info, 'address')}`
Amount: `{user_info['amount'] if 'amount' in user_info else '0.1'}`
Memo/ExtraID: `{user_info['memo'] if 'memo' in user_info else '0'}`"""

def text_transaction_type(user_info):
    return f"""
*Transaction Type*

Donation: {user_info['donation'] if 'donation' in user_info else 'False'}
Remove Direct-Pay: {user_info['direct'] if 'direct' in user_info else 'False'}
Allow to edit amount: {user_info['editable'] if 'editable' in user_info else 'False'}
Simpler checkout: {user_info['simple'] if 'simple' in user_info else 'True'}"""

def text_ui(user_info):
    return f"""
*UI & Appearance*

Name: {display_if_set(user_info, 'name')}
Description: {display_if_set(user_info, 'description')}
Button color: `{user_info['buttonbgcolor'] if 'buttonbgcolor' in user_info else 'ff3c00'}`
Text color: `{user_info['textcolor'] if 'textcolor' in user_info else 'fffff'}`
Widget Background: {user_info['bgcolor'] if 'bgcolor' in user_info else 'False'}"""

def text_other(user_info):
    return f"""
*Additional*

Default coin: {user_info['ticker_from'] if 'ticker_from' in user_info else 'BTC'}
Default network: {user_info['network_from'] if 'network_from' in user_info else 'Mainnet'}
Trocador referral: {display_if_set(user_info, 'referral')}
Fiat equivalent: {display_if_set(user_info, 'fiat')}
Notification email: {display_if_set(user_info, 'email')}
Minimum KYC score (A, B or C): {display_if_set(user_info, 'logpolicy')}
Webhook: {display_if_set(user_info, 'webhook')}"""