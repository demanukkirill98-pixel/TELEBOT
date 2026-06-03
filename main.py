import telebot
import mysql.connector
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8838879301:AAFw7eSCyU1UPQRxD0y-geppxpwDDWFgGIc"

# Для локального запуска (на том же сервере, где MySQL)
db_config = {
    'host': 'localhost',  # или 127.0.0.1, но localhost предпочтительнее
    'user': 'gs341801',
    'password': 'X0w20ypr9q0B',
    'database': 'gs341801'
}

bot = telebot.TeleBot(TOKEN)

# Хранилище состояний пользователей
user_states = {}

def update_admin_level(player_name, new_level):
    """Обновляет уровень администратора в таблице account"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Проверяем структуру таблицы
        cursor.execute("SHOW COLUMNS FROM account")
        columns = [col[0] for col in cursor.fetchall()]
        
        # Определяем поле с именем игрока
        if 'username' in columns:
            name_field = 'username'
        elif 'name' in columns:
            name_field = 'name'
        elif 'nick' in columns:
            name_field = 'nick'
        elif 'player' in columns:
            name_field = 'player'
        else:
            return False, f"❌ Поле с именем не найдено. Доступно: {columns}"
        
        # Определяем поле с админ-уровнем
        if 'admin' in columns:
            admin_field = 'admin'
        elif 'admin_level' in columns:
            admin_field = 'admin_level'
        elif 'admin_lvl' in columns:
            admin_field = 'admin_lvl'
        else:
            return False, f"❌ Поле admin не найдено. Доступно: {columns}"
        
        # Выполняем обновление
        query = f"UPDATE account SET {admin_field} = %s WHERE {name_field} = %s"
        cursor.execute(query, (new_level, player_name))
        conn.commit()
        
        if cursor.rowcount > 0:
            return True, f"✅ {player_name} получил {new_level} уровень админа"
        else:
            return False, f"❌ Игрок {player_name} не найден в базе"
        
    except mysql.connector.Error as e:
        return False, f"❌ Ошибка MySQL: {e}"
    except Exception as e:
        return False, f"❌ Ошибка: {e}"
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

def get_level_keyboard():
    """Клавиатура с уровнями 1-13"""
    markup = InlineKeyboardMarkup(row_width=4)
    buttons = []
    for i in range(1, 14):
        buttons.append(InlineKeyboardButton(str(i), callback_data=f"level_{i}"))
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎖️ Выдать админку", callback_data="give_admin"))
    bot.reply_to(
        message, 
        "👋 Добро пожаловать!\n\n"
        "Я бот для выдачи администраторских прав на SAMP сервере.\n\n"
        "Нажмите кнопку, чтобы выдать админку:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "give_admin")
def ask_nickname(call):
    user_states[call.from_user.id] = "waiting_nick"
    bot.edit_message_text(
        "📝 Введите ник игрока:",
        call.message.chat.id,
        call.message.message_id
    )

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_nick")
def get_nickname(message):
    # Сохраняем ник и переходим к выбору уровня
    user_states[message.from_user.id] = {"state": "waiting_level", "nick": message.text.strip()}
    
    bot.reply_to(
        message,
        f"📛 Игрок: {message.text}\n\n"
        f"🎖️ Теперь выберите уровень админки (1-13):",
        reply_markup=get_level_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("level_"))
def set_level(call):
    level = int(call.data.split("_")[1])
    user_data = user_states.get(call.from_user.id)
    
    if not user_data or user_data.get("state") != "waiting_level":
        bot.answer_callback_query(call.id, "❌ Начните сначала: /start")
        return
    
    player_name = user_data["nick"]
    
    # Выдаём админку
    success, msg = update_admin_level(player_name, level)
    
    # Очищаем состояние пользователя
    user_states.pop(call.from_user.id, None)
    
    # Отправляем результат
    bot.edit_message_text(
        msg,
        call.message.chat.id,
        call.message.message_id
    )
    
    # Показываем кнопку для выдачи следующему игроку
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎖️ Выдать ещё", callback_data="give_admin"))
    bot.send_message(
        call.message.chat.id, 
        "Хотите выдать админку ещё одному игроку?",
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(
        message,
        "📋 Команды:\n"
        "/start - начать работу\n"
        "/help - эта справка\n\n"
        "После /start нажмите кнопку 'Выдать админку'\n"
        "1. Введите ник игрока\n"
        "2. Выберите уровень (1-13)"
    )

print("✅ Админ-бот успешно запущен!")
print("Ожидание сообщений...")
bot.polling(none_stop=True)
