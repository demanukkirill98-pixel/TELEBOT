import telebot
import mysql.connector
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8838879301:AAFw7eSCyU1UPQRxD0y-geppxpwDDWFgGIc"

db_config = {
    'host': '127.0.0.1',
    'user': 'gs341801',
    'password': 'X0w20ypr9q0B',
    'database': 'gs341801'
}

bot = telebot.TeleBot(TOKEN)

user_states = {}

def update_admin_level(player_name, new_level):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("SHOW COLUMNS FROM account")
        columns = [col[0] for col in cursor.fetchall()]
        
        if 'username' in columns:
            name_field = 'username'
        elif 'name' in columns:
            name_field = 'name'
        elif 'nick' in columns:
            name_field = 'nick'
        else:
            return False, "Поле с именем не найдено"
        
        if 'admin' in columns:
            admin_field = 'admin'
        elif 'admin_level' in columns:
            admin_field = 'admin_level'
        else:
            return False, "Поле admin не найдено"
        
        query = f"UPDATE account SET {admin_field} = %s WHERE {name_field} = %s"
        cursor.execute(query, (new_level, player_name))
        conn.commit()
        
        if cursor.rowcount > 0:
            return True, f"✅ {player_name} получил {new_level} уровень админа"
        else:
            return False, f"❌ Игрок {player_name} не найден"
        
    except Exception as e:
        return False, f"❌ Ошибка БД: {e}"
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

def get_level_keyboard():
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
    bot.reply_to(message, "👋 Добро пожаловать!\n\nНажмите кнопку, чтобы выдать админку:", reply_markup=markup)

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
    user_states[message.from_user.id] = {"state": "waiting_level", "nick": message.text}
    
    bot.reply_to(
        message,
        f"📛 Игрок: {message.text}\n\n🎖️ Теперь выберите уровень админки (1-13):",
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
    success, msg = update_admin_level(player_name, level)
    user_states.pop(call.from_user.id, None)
    
    bot.edit_message_text(msg, call.message.chat.id, call.message.message_id)
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎖️ Выдать ещё", callback_data="give_admin"))
    bot.send_message(call.message.chat.id, "Хотите выдать ещё?", reply_markup=markup)

print("✅ Админ-бот запущен!")
bot.polling()
