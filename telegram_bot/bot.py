import telebot
import json
import requests
from configuration import BOT_TOKEN, ADMIN_USERNAME, ADMIN_PASSWORD, CHAT_ID
from telegram_menu import BaseMessage, TelegramMenuSession, NavigationHandler


bot = telebot.TeleBot(BOT_TOKEN)

#defining settings controllable by the bot
litter_settings = '{"sampling_rate": {"value": 1000}, "use_counter": {"value": 3}, "used_offset": {"value": 5}, "tare_timeout": {"value": 10}, "danger_threshold": {"value": 1}, "danger_counter": {"value": 1}}}'
settings=json.loads(litter_settings)



@bot.message_handler(commands=['start'])
def send_welcome(message):
    if str(message.chat.id) != CHAT_ID:
        return
    bot.reply_to(message, "Hi, PurrfectPotty bot here. You can use me to receive notifications about the status of "
                          "your cat's litterbox, or change parameters of the smart litterbox.")

def send_sampling_rate(message):
    if str(message.chat.id) != CHAT_ID:
        return
    bot.reply_to(message, "Current sampling rate is " + str(settings['sampling_rate']['value']) + " seconds.")

class StartMessage(BaseMessage):
    """Start menu, create all app sub-menus."""

    LABEL = "start"

    def __init__(self, navigation: NavigationHandler) -> None:
        """Init StartMessage class."""
        super().__init__(navigation, StartMessage.LABEL)
        second_menu = SecondMenuMessage(navigation)
        self.add_button(label="Settings", callback=second_menu)

    def update(self) -> str:
        """Update message content."""
        return "Hello, world!"

class SecondMenuMessage(BaseMessage):
    """Second menu, create an inlined button."""

    LABEL = "action"

    def __init__(self, navigation: NavigationHandler) -> None:
        """Init SecondMenuMessage class."""
        super().__init__(navigation, StartMessage.LABEL, inlined=True)

        # 'run_and_notify' function executes an action and return a string as Telegram notification.
        self.add_button(label="set sampling rate", callback=self.run_and_notify("sampling_rate"))
        # 'run_and_notify' function executes an action and return a string as Telegram notification.
        self.add_button(label="set tare timeout", callback=self.run_and_notify("tare_timeout"))
        # 'run_and_notify' function executes an action and return a string as Telegram notification.
        self.add_button(label="set danger threshold", callback=self.run_and_notify("danger_threshold"))
        # 'run_and_notify' function executes an action and return a string as Telegram notification.
        self.add_button(label="set danger counter", callback=self.run_and_notify("danger_counter"))
        # 'run_and_notify' function executes an action and return a string as Telegram notification.
        self.add_button(label="set use counter", callback=self.run_and_notify("use_counter"))
        # 'run_and_notify' function executes an action and return a string as Telegram notification.
        self.add_button(label="set used offset", callback=self.run_and_notify("used_offset"))
        # 'back' button goes back to previous menu
        self.add_button_back()
        # 'home' button goes back to main menu
        self.add_button_home()

    def update(self) -> str:
        """Update message content."""
        # emoji can be inserted with a keyword enclosed with ::
        # list of emojis can be found at this link: https://www.webfx.com/tools/emoji-cheat-sheet/
        return ":warning: Second message"

    @staticmethod
    def set_sampling_rate(message):
        if message.text.isdigit() == False:
            bot.reply_to(message, "Sampling rate must be a number.")
            return
        requests.post('http://API_URI:5000/set_sampling_rate', json={"sampling_rate": message.text})
        settings['sampling_rate']['value'] = message.text
        return "Sampling rate set to " + message.text + " seconds."
    
    def set_tare_timeout(message):
        if message.text.isdigit() == False:
            bot.reply_to(message, "Sampling rate must be a number.")
            return
        requests.post('http://API_URI:5000/set_tare_timeout', json={"tare_timeout": message.text})
        settings['tare_timeout']['value'] = message.text
        return "Tare timeout set to " + message.text + " seconds."
    
    def set_danger_threshold(message):
        if message.text.isdigit() == False:
            bot.reply_to(message, "Sampling rate must be a number.")
            return
        requests.post('http://API_URI:5000/set_danger_threshold', json={"danger_threshold": message.text})
        settings['danger_threshold']['value'] = message.text
        return "Danger threshold set to " + message.text + " grams."
    
    def set_danger_counter(message):
        if message.text.isdigit() == False:
            bot.reply_to(message, "Sampling rate must be a number.")
            return
        requests.post('http://API_URI:5000/set_danger_counter', json={"danger_counter": message.text})
        settings['danger_counter']['value'] = message.text
        return "Danger counter set to " + message.text + " times."
    
    def set_use_counter(message):
        if message.text.isdigit() == False:
            bot.reply_to(message, "Sampling rate must be a number.")
            return
        requests.post('http://API_URI:5000/set_use_counter', json={"use_counter": message.text})
        settings['use_counter']['value'] = message.text
        return "Use counter set to " + message.text + " times."
    
    def set_used_offset(message):
        if message.text.isdigit() == False:
            bot.reply_to(message, "Sampling rate must be a number.")
            return
        requests.post('http://API_URI:5000/set_used_offset', json={"used_offset": message.text})
        settings['used_offset']['value'] = message.text
        return "Used offset set to " + message.text + " grams."
    
    def run_and_notify(action: str) -> str:
        #take user input from telegram message interface
        # send the input to the API
        # update the settings dictionary
        # return a string to be sent as a message
        message = message.text
        msg = message.text.isdigit()
        if msg == False:
            bot.reply_to(message, "Sampling rate must be a number.")
            return 
        if action == "sampling_rate":
            return set_sampling_rate(message)
        elif action == "tare_timeout":
            return set_tare_timeout(message)
        elif action == "danger_threshold":
            return set_danger_threshold(message)
        elif action == "danger_counter":
            return set_danger_counter(message)
        elif action == "use_counter":
            return set_use_counter(message)
        elif action == "used_offset":
            return set_used_offset(message)
        else:
            return "Error"



    
        if message.text.isdigit() == False:
            bot.reply_to(message, "Sampling rate must be a number.")
            return
        requests.post('http://API_URI:5000/set_used_offset', json={"used_offset": message.text})
        settings['used_offset']['value'] = message.text
        return "Used offset set to " + message.text + " grams."
    


TelegramMenuSession(BOT_TOKEN).start(StartMessage)



print("Bot is now running...")
bot.infinity_polling()


