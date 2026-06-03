import telebot

TOKEN = "31a7d83f-000f-5000-b000-12dfae03c170"
USERNAME = "@Mutriop"
TEXT = "Привет сучара"

bot = telebot.TeleBot(TOKEN)

try:
    bot.send_message(USERNAME, TEXT)
    print("✅ Сообщение отправлено")
except Exception as e:
    print(f"❌ Ошибка: {e}")
