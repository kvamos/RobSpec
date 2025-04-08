from telebot import TeleBot, types
import DataBase as db
import keyboards
import support



def home_student(bot: TeleBot, user_id: int):
    """Отображает домашнюю страницу исполнителя"""
    
    student_data = db.get_student_data(user_id=user_id)
    active_project = db.get_student_active_projects(student_id=user_id)

    message = (
    "<b>🛠️ Ваш профиль исполнителя</b>\n\n"
    f"💰 <b>Баланс:</b> <code>{student_data['balance']}₽</code>\n"
    f"⭐ <b>Рейтинг:</b> <code>{student_data['rating']}/5.0</code>\n"
    f"📂 <b>Активные проекты:</b> <code>{len(active_project)}</code>\n\n"
)
    if len(active_project) == 0:
        message +='У вас пока нет проектов'
        
    else:
        message += "<b>🔍 Текущие проекты:</b>\n"
        for i , project in enumerate(active_project[:3] , 1):
            project_title = db.get_project_info(project , 'title')
            message += f'{i}.{project_title}'
    
    bot.send_message(
        user_id , 
        message , 
        parse_mode="HTML" ,
        reply_markup = keyboards.home_student_keyboard()
    )




def register_student_handlers(bot: TeleBot):
    pass