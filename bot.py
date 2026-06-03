import telebot

# Замените на ваш реальный токен
TOKEN = "8838879301:AAFw7eSCyU1UPQRxD0y-geppxpwDDWFgGIc"

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, и я отвечаю на команды.")

# Обработчик команды /hello
@bot.message_handler(commands=['hello'])
def say_hello(message):
    bot.reply_to(message, f"Привет, {message.from_user.first_name}!")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Вы написали: {message.text}")

# Запуск бота
print("✅ Бот успешно запущен и ожидает сообщения...")
bot.polling()
