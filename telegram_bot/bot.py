import telebot
from telebot import types
import json
import requests
from configuration import BOT_TOKEN, ADMIN_USERNAME, ADMIN_PASSWORD, CHAT_ID, API_URI


# defining settings controllable by the bot

def login():
    ans = requests.post(f"{API_URI}/token",
                        data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD, "grant_type": "password"})
    ans = ans.json()
    return f"Bearer {ans['access_token']}"


settings = requests.get(f'{API_URI}/api/settings/v1', headers={"Authorization": login()})
settings = settings.json()

# Init the  bot with token
bot = telebot.TeleBot(BOT_TOKEN)
user_register_dict = {}

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
            ['sampling_rate', 'use_counter', 'used_offset', 'tare_timeout',
             'back'], markup)
        message = bot.reply_to(message,
                               "Coming right up!",
                               reply_markup=markup)
        bot.register_next_step_handler(message, get_value_handler)
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

#user input handler
def get_value_handler(message):
    # telling the user his previous choice
    choice = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    if choice == 'sampling_rate':
        markup = generate_buttons(['Back'], markup)
        message = bot.reply_to(message, f"you choose {choice}... Send me a message containing a number with / before it (e.g. /2).. Please make sure it is an integer value.",
                        reply_markup=markup)
        bot.register_next_step_handler(message, set_config_sampling_rate)
    elif choice == 'use_counter':
        message = bot.reply_to(message, f"you choose {choice}... Send me a message containing a number with / before it (e.g. /2).. Please make sure it is an integer value.",
                        reply_markup=markup)
        bot.register_next_step_handler(message, set_config_use_counter)
    elif choice == 'used_offset':
        message = bot.reply_to(message, f"you choose {choice}... Send me a message containing a number with / before it (e.g. /2).. Please make sure it is an integer value.",
                        reply_markup=markup)
        bot.register_next_step_handler(message, set_config_used_offset)
    elif choice == 'tare_timeout':
        message = bot.reply_to(message, f"you choose {choice}... Send me a message containing a number with / before it (e.g. /2).. Please make sure it is an integer value.",
                        reply_markup=markup)
        bot.register_next_step_handler(message, set_config_tare_timeout)
    elif choice == 'back':
        markup = generate_buttons(['Get Configuration', 'Set Configuration'], markup)
        message = bot.reply_to(message, f"Going {choice} to main menu",
                        reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)


# request to server to set new configuration
def set_config_sampling_rate(message):
    value = message.text.replace('/', '')
    if value.isdigit():
        print(value)
        res = call_to_set('sampling_rate', value)
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Back'], markup)
        if res == 200:
            message = bot.reply_to(message, "settings was changed", reply_markup=markup)
            bot.register_next_step_handler(message, main_menu_handler)
        else:
            message= bot.reply_to(message, "something went wrong", reply_markup=markup)
            bot.register_next_step_handler(message, main_menu_handler)
    else:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Set Configuration', 'Get Configuration'], markup)
        message = bot.reply_to(message, "I cant understand you. What you want to do?", reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)

def set_config_use_counter(message):
    value = message.text.replace('/', '')
    if value.isdigit():
        print(value)
        res = call_to_set('use_counter', value)
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Back'], markup)
        if res == 200:
            message = bot.reply_to(message, "settings was changed", reply_markup=markup)
            bot.register_next_step_handler(message, main_menu_handler)
        else:
            message= bot.reply_to(message, "something went wrong", reply_markup=markup)
            bot.register_next_step_handler(message, main_menu_handler)
    else:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Set Configuration', 'Get Configuration'], markup)
        message = bot.reply_to(message, "I cant understand you. What you want to do?", reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)

def set_config_used_offset(message):
    value = message.text.replace('/', '')
    if value.isdigit():
        print(value)
        res = call_to_set('used_offset', value)
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Back'], markup)
        if res == 200:
            message = bot.reply_to(message, "settings was changed", reply_markup=markup)
            bot.register_next_step_handler(message, main_menu_handler)
        else:
            message= bot.reply_to(message, "something went wrong", reply_markup=markup)
            bot.register_next_step_handler(message, main_menu_handler)
    else:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Set Configuration', 'Get Configuration'], markup)
        message = bot.reply_to(message, "I cant understand you. What you want to do?", reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)

def set_config_tare_timeout(message):
    value = message.text.replace('/', '')
    if value.isdigit():
        print(value)
        res = call_to_set('tare_timeout', value)
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Back'], markup)
        if res == 200:
            message = bot.reply_to(message, "settings was changed", reply_markup=markup)
            bot.register_next_step_handler(message, main_menu_handler)
        else:
            message= bot.reply_to(message, "something went wrong", reply_markup=markup)
            bot.register_next_step_handler(message, main_menu_handler)
    else:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Set Configuration', 'Get Configuration'], markup)
        message = bot.reply_to(message, "I cant understand you. What you want to do?", reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)

def set_config_danger_threshold(message):
    value = message.text.replace('/', '')
    if value.isdigit():
        print(value)
        res = call_to_set('danger_threshold', value)
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Back'], markup)
        if res == 200:
            message = bot.reply_to(message, "settings was changed", reply_markup=markup)
            bot.register_next_step_handler(message, main_menu_handler)
        else:
            message= bot.reply_to(message, "something went wrong", reply_markup=markup)
            bot.register_next_step_handler(message, main_menu_handler)
    else:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Set Configuration', 'Get Configuration'], markup)
        message = bot.reply_to(message, "I cant understand you. What you want to do?", reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)

def set_config_danger_counter(message):
    value = message.text.replace('/', '')
    if value.isdigit():
        print(value)
        res = call_to_set('danger_counter', value)
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Back'], markup)
        if res == 200:
            message = bot.reply_to(message, "settings was changed", reply_markup=markup)
            bot.register_next_step_handler(message, main_menu_handler)
        else:
            message= bot.reply_to(message, "something went wrong", reply_markup=markup)
            bot.register_next_step_handler(message, main_menu_handler)
    else:
        markup = types.ReplyKeyboardMarkup(row_width=2)
        markup = generate_buttons(['Set Configuration', 'Get Configuration'], markup)
        message = bot.reply_to(message, "I cant understand you. What you want to do?", reply_markup=markup)
        bot.register_next_step_handler(message, main_menu_handler)

def call_to_set(what, value):
    settings = requests.get(f'{API_URI}/api/settings/v1', headers={"Authorization": login()})
    settings = settings.json()
    settings[what] = int(value)
    print(settings)
    snd = json.dumps(settings)
    response = requests.put(f'{API_URI}/api/settings/v1', headers={"Authorization": login(), "accept": "application/json", "Content-Type": "application/json"},
                      data=snd)
    print (response.content)
    return response.status_code
# request to the server to get the current settings
def get_settings():
    settings = requests.get(f'{API_URI}/api/settings/v1', headers={"Authorization": login()})
    settings = settings.json()
    text_settings = f"""sampling_rate: {settings['sampling_rate']} \n
    use_counter: {settings['use_counter']} \n  
    used_offset: {settings['used_offset']} \n
    tare_timeout: {settings['tare_timeout']} \n"""
    return text_settings


# Launches the bot in infinite loop mode with additional
# ...exception handling, which allows the bot
# ...to work even in case of errors.
bot.infinity_polling()
