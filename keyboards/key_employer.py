from telebot import types

def home_employer_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add("➕ Новый проект", "📂 Мои проекты")
    keyboard.add("👥 Отклики", "💳 пополнить баланс")
    return keyboard



def projects_navigator_employer(current_index, total_projects, all_projects):
    # Кнопка "назад"
    if current_index > 0:
        prev_id = all_projects[current_index - 1]
        btn_back = types.InlineKeyboardButton(
            "⏮️ назад", 
            callback_data=f"employer_project_prev_{prev_id}_{current_index-1}"
        )
    else:
        btn_back = types.InlineKeyboardButton(
            "⏮️ назад", 
            callback_data="employer_project_boundary_first"
        )
    
    # Кнопка "вперед"
    if current_index < total_projects - 1:
        next_id = all_projects[current_index + 1]
        btn_next = types.InlineKeyboardButton(
            "вперёд ⏭️", 
            callback_data=f"employer_project_next_{next_id}_{current_index+1}"
        )
    else:
        btn_next = types.InlineKeyboardButton(
            "вперёд ⏭️", 
            callback_data="employer_project_boundary_last"
        )

    return [btn_back, btn_next]  # Возвращаем список кнопок