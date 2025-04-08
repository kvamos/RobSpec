from telebot import types

def role_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add("📢 Заказчик", "🧑‍💻 Исполнитель")
    return keyboard