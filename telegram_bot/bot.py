import telebot
from telebot import types
import json
import requests
from configuration import BOT_TOKEN, ADMIN_USERNAME, ADMIN_PASSWORD, CHAT_ID, API_URI


# defining settings controllable by the bot

def login():
    ans = requests.post(f"http://{API_URI}/token",
                        data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD, "grant_type": "password"})
    ans = ans.json()
    return f"Bearer {ans['access_token']}"


settings = requests.get(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()})
settings = settings.json()

# Init the  bot with token
bot = telebot.TeleBot(BOT_TOKEN)


# parse number from message
def extract_number(text):
    return text.split()[1].strip()


# Button generator
def generate_buttons(bts_names, markup):
    for button in bts_names:
        markup.add(types.KeyboardButton(button))
    return markup


# Bot start handler
@bot.message_handler(commands=['start'])
def send_hello(message):
    # Init keyboard markup
    markup = types.ReplyKeyboardMarkup(row_width=2)
    # Add to buttons by list with ours generate_buttons function.
    markup = generate_buttons(['Get Configuration', 'Set Configuration'], markup)
    message = bot.reply_to(message, """Hi there! What you want to do?""",
                           reply_markup=markup)

    # Here we assign the next handler function and pass in our response from the user.
    bot.register_next_step_handler(message, main_menu_handler)


# Here we no longer need to specify the decorator function
def main_menu_handler(message):
    if message.text == 'Set Configuration':
        markup = types.ReplyKeyboardMarkup(row_width=3)
        markup = generate_buttons(
            ['sampling_rate', 'use_counter', 'used_offset', 'tare_timeout', 'danger_threshold', 'danger_counter',
             'back'], markup)
        message = bot.reply_to(message,
                               "Coming right up!",
                               reply_markup=markup)
        bot.register_next_step_handler(message, set_config)
    elif message.text == 'Get Configuration':
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Back'], markup)
        message = bot.reply_to(message,
                               get_settings(),
                               reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)
    elif message.text == 'Back':
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Set Configuration', 'Get Configuration'], markup)
        message = bot.reply_to(message,
                               "Right away!",
                               reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)
    else:
        # Sometimes user dont want to use keyboard markup, so we need to deal with it
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Set Configuration', 'Get Configuration'], markup)
        message = bot.reply_to(message,
                               "I cant understand you. What you want to do?",
                               reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)


# request to server to set new configuration
def set_config(message):
    if message == 'sampling_rate':
        requests.post(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()},
                      data={"sampling_rate": extract_number(message.text)})
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Back'], markup)
        message = bot.reply_to(message, "sampling_rate was changed", reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)
    elif message == 'use_counter':
        requests.post(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()},
                      data={"use_counter": extract_number(message.text)})
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Back'], markup)
        message = bot.reply_to(message, "use_counter was changed", reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)
    elif message == 'used_offset':
        requests.post(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()},
                      data={"used_offset": extract_number(message.text)})
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Back'], markup)
        message = bot.reply_to(message, "used_offset was changed", reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)
    elif message == 'tare_timeout':
        requests.post(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()},
                      data={"tare_timeout": extract_number(message.text)})
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Back'], markup)
        message = bot.reply_to(message, "tare_timeout was changed", reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)
    elif message == 'danger_threshold':
        requests.post(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()},
                      data={"danger_threshold": extract_number(message.text)})
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Back'], markup)
        message = bot.reply_to(message, "danger_threshold was changed", reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)
    elif message == 'danger_counter':
        requests.post(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()},
                      data={"danger_counter": extract_number(message.text)})
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Back'], markup)
        message = bot.reply_to(message, "danger_counter was changed", reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)
    else:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Set Configuration', 'Get Configuration'], markup)
        message = bot.reply_to(message, "I cant understand you. What you want to do?", reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)


# request to the server to get the current settings
def get_settings():
    settings = requests.get(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()})
    settings = settings.json()
    text_settings = f"""sampling_rate: {settings['sampling_rate']} \n
                    use_counter: {settings['use_counter']} \n  
                    used_offset: {settings['used_offset']} \n
                    tare_timeout: {settings['tare_timeout']} \n
                    danger_threshold: {settings['danger_threshold']} \n
                    danger_counter: {settings['danger_counter']} \n"""
    return text_settings


# Launches the bot in infinite loop mode with additional
# ...exception handling, which allows the bot
# ...to work even in case of errors.
bot.infinity_polling()
