import telebot

TOKEN = "8838879301:AAFw7eSCyU1UPQRxD0y-geppxpwDDWFgGIc"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def say_hello(message):
    bot.reply_to(message, "Привет")

print("✅ Бот запущен!")
bot.polling()
