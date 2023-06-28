import telebot
from configuration import BOT_TOKEN, ADMIN_USERNAME, ADMIN_PASSWORD, CHAT_ID

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if str(message.chat.id) != CHAT_ID:
        return
    bot.reply_to(message, "Hi, PurrfectPotty bot here. You can use me to receive notifications about the status of "
                          "your cat's litterbox, or change parameters of the smart litterbox.")


bot.infinity_polling()