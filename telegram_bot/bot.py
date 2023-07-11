import telebot
import json
import requests
from configuration import BOT_TOKEN, ADMIN_USERNAME, ADMIN_PASSWORD, CHAT_ID, API_URI
from telegram_menu import BaseMessage, TelegramMenuSession, NavigationHandler

bot = telebot.TeleBot(BOT_TOKEN)


# defining settings controllable by the bot

def login():
    ans = requests.post(f"http://{API_URI}/token",
                        data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD, "grant_type": "password"})
    ans = ans.json()
    return f"Bearer {ans['access_token']}"


settings = requests.get(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()})
settings = settings.json()


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
        # 'get info' button returns a string as Telegram notification.
        self.add_button(label="get info", callback=self.get_info(message="info"))
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
    def set_sampling_rate(self, message) -> str:
        if not message.text.isdigit():
            bot.reply_to(message, "Sampling rate must be a number.")
            return
        requests.post(f'http://{API_URI}/set_sampling_rate', headers={"Authorization": login()}, json={"sampling_rate": message.text})
        settings['sampling_rate']['value'] = message.text
        return "Sampling rate set to " + message.text + " seconds."

    def set_tare_timeout(self, message) -> str:
        if not message.text.isdigit():
            bot.reply_to(message, "Setting value must be a number.")
            return ""
        json_info = requests.get(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()})
        json_info['litter']['tare_timeout']['value'] = message.text
        requests.post(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()}, json=json_info)
        settings['tare_timeout']['value'] = message.text
        return "Tare timeout set to " + message.text + " seconds."

    def set_danger_threshold(self, message) -> str:
        if not message.text.isdigit():
            bot.reply_to(message, "Setting value must be a number.")
            return
        json_info = requests.get(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()})
        json_info['litter']['danger_threshold']['value'] = message.text
        requests.post(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()}, json=json_info)
        settings['danger_threshold']['value'] = message.text
        return "Danger threshold set to " + message.text + " grams."

    def set_danger_counter(self, message) -> str:
        if not message.text.isdigit():
            bot.reply_to(message, "Setting value must be a number.")
            return
        json_info = requests.get(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()})
        json_info['litter']['danger_counter']['value'] = message.text
        requests.post(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()}, json=json_info)
        settings['danger_counter']['value'] = message.text
        return "Danger counter set to " + message.text + " times."

    def set_use_counter(self, message) -> str:
        if not message.text.isdigit():
            bot.reply_to(message, "Setting value must be a number.")
            return
        json_info = requests.get(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()})
        json_info['litter']['use_counter']['value'] = message.text
        requests.post(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()}, json=json_info)
        settings['use_counter']['value'] = message.text
        return "Use counter set to " + message.text + " times."

    def set_used_offset(self, message) -> str:
        if not message.text.isdigit():
            bot.reply_to(message, "Setting value must be a number.")
            return
        json_info = requests.get(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()})
        json_info['litter']['used_offset']['value'] = message.text
        requests.post(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()}, json=json_info)
        settings['used_offset']['value'] = message.text
        return "Used offset set to " + message.text + " grams."

    def run_and_notify(self, message, action: str) -> str:
        # take user input from telegram message interface
        # send the input to the API
        # update the settings dictionary
        # return a string to be sent as a message
        message = message.text
        msg = message.text.isdigit()
        if not msg:
            bot.reply_to(message, "Sampling rate must be a number.")
            return
        if not message.text.isdigit():
            bot.reply_to(message, "Setting value must be a number.")
            return
        if action == "sampling_rate":
            return self.set_sampling_rate(message)
        elif action == "tare_timeout":
            return self.set_tare_timeout(message)
        elif action == "danger_threshold":
            return self.set_danger_threshold(message)
        elif action == "danger_counter":
            return self.set_danger_counter(message)
        elif action == "use_counter":
            return self.set_use_counter(message)
        elif action == "used_offset":
            return self.set_used_offset(message)
        else:
            return "Error"

    def get_info(self, message) -> str:
        # get the info from the API
        json_info = requests.get(f'http://{API_URI}/api/settings/v1', headers={"Authorization": login()})
        textualized_info = ("Current settings:\n", "Sampling rate: ",
                            json_info['sampling_rate']["value"], " ms\n",
                            "Tare timeout: ", json_info['tare_timeout']["value"],
                            " seconds\n", "Danger threshold: ", json_info['danger_threshold']["value"], " grams\n",
                            "Danger counter: ", json_info['danger_counter']["value"], " times\n",
                            "Use counter: ", json_info['use_counter']["value"], " times\n",
                            "Used offset: ", json_info['used_offset']["value"], " grams\n")
        # return a string to be sent as a message
        txt = ""
        for elem in textualized_info:
            txt += elem
        bot.reply_to(message, txt)
        return txt


print("Bot is now running...")
TelegramMenuSession(BOT_TOKEN).start(StartMessage)