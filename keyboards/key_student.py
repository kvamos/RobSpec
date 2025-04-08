from telebot import types


def home_student_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True , one_time_keyboard=True)
    keyboard.add("🔍 Найти проекты", "📌 Мои заявки")
    keyboard.add('📁мои проекты' , "🤑 вывести баланс")
    return keyboard