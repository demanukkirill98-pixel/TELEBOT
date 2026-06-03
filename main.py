import telebot
import asyncio
from samp_py.client import SampClient

TOKEN = "8838879301:AAFw7eSCyU1UPQRxD0y-geppxpwDDWFgGIc"

RCON_HOST = "54.38.117.74"
RCON_PORT = 1305
RCON_PASSWORD = "ndsoidhh3j9888fuh8ej"

bot = telebot.TeleBot(TOKEN)

def execute_rcon(command):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def send_rcon():
            async with SampClient(address=RCON_HOST, port=RCON_PORT, rcon_password=RCON_PASSWORD) as client:
                result = await client.send_rcon_command(command)
                return result if result else "✅ Выполнено"
        
        return loop.run_until_complete(send_rcon())
    except Exception as e:
        return f"❌ Ошибка: {e}"

@bot.message_handler(commands=['setadmins'])
def set_admins(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "❌ /setadmins [ник] [уровень]")
            return
        
        nick = parts[1]
        level = parts[2]
        
        if not level.isdigit() or int(level) < 0 or int(level) > 13:
            bot.reply_to(message, "❌ Уровень 0-13")
            return
        
        result = execute_rcon(f"setadmins {nick} {level}")
        bot.reply_to(message, f"✅ {nick} - {level} уровень\n\n{result}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎮 /setadmins [ник] [уровень]")

print("✅ Бот запущен!")
bot.polling()
