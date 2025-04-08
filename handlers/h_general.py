from telebot import types
from telebot import TeleBot
import logging
import DataBase as db
import support
import keyboards

logger = logging.getLogger(__name__)

def register_general_handlers(bot: TeleBot):
    @bot.message_handler(commands=['start' , 'home'])
    def handle_start(msg):
        try:
            if not db.user_exists(msg.from_user.id):
                bot.delete_state(msg.from_user.id, msg.chat.id)
                bot.set_state(msg.from_user.id, "add_user", msg.chat.id)
                
                message = (
                    "<b>👋 Привет!</b> Добро пожаловать в платформу для поиска проектов и исполнителей!\n\n"
                "Здесь <b>заказчики</b> находят исполнителей, а <b>исполнители</b> — интересные задачи.\n\n"
                "🔎 <i>Давайте начнём!</i>\n"
                "Кто вы?\n\n"
                "👇 Выберите одну из ролей:\n"
                "▪️ <b>Заказчик</b> — хочу разместить проект\n"
                "▪️ <b>Исполнитель</b> — ищу интересные задачи"
                )
                
                bot.send_message(
                    msg.chat.id ,
                    message , 
                    parse_mode="HTML" ,
                    reply_markup=keyboards.role_keyboard()
                    )
                
                bot.register_next_step_handler(msg, process_role_selection)
                
            else:
                support.show_home(bot=bot , user_id=msg.from_user.id)
        
        except Exception as e:
            logger.error(f'Error in handle_start:{e}')
            

    def process_role_selection(msg):
        try:
            if msg.text not in ["📢 Заказчик", "🧑‍💻 Исполнитель"]:
                message = (
                    "<b>❗ Пожалуйста, выберите вашу роль:</b>\n\n"
                    "👇 Нажмите одну из кнопок ниже, чтобы продолжить:\n"
                    "▪️ <b>💼 Заказчик</b> — хочу разместить проект\n"
                    "▪️ <b>🛠️ Исполнитель</b> — ищу задачи для выполнения"
                )
                
                bot.send_message(
                    msg.chat.id , 
                    message , 
                    parse_mode="HTML"
                    )
                
                return bot.register_next_step_handler(msg , process_role_selection)
            
            else:
                if msg.text == "📢 Заказчик":
                    bot.add_data(msg.from_user.id , msg.chat.id , role = 'employer')
                    
                else:
                    bot.add_data(msg.from_user.id , msg.chat.id , role = 'student')

                message = (
                    "<b>📝 Укажите, пожалуйста, ваше ФИО:</b>\n"
                    "Это поможет сделать ваш профиль более надёжным и понятным для других пользователей."
                )

                bot.send_message(
                    msg.chat.id , 
                    message , 
                    parse_mode='HTML' ,
                    reply_markup=types.ReplyKeyboardRemove()
                    )
                
                bot.register_next_step_handler(msg , process_fullname_selection)
        
        except Exception as e:
            logger.error(f'error in process_role_selection')
    
    
    def process_fullname_selection(msg):
        try:
            fullname = msg.text.split()
            if len(fullname) < 2:
                message = (
                    "<b>⚠️ Похоже, вы ввели некорректное ФИО.</b>\n\n"
                    "Пожалуйста, укажите <b>как минимум два слова</b> — например: <i>Иван Петров</i>.\n"
                    "Это нужно для вашего профиля и доверия со стороны других пользователей."
                )
                
                bot.send_message(
                    msg.chat.id , 
                    message , 
                    parse_mode='HTML'
                )
                
                return bot.register_next_step_handler(process_fullname_selection)
            
            else:
                with bot.retrieve_data(msg.from_user.id , msg.chat.id) as data:
                    
                    db.add_user(
                        user_id=msg.from_user.id , 
                        username=msg.from_user.username , 
                        full_name=msg.text , 
                        role=data['role']
                        )
                    
                    message = ''
                    
                    if data['role'] == 'employer':
                        message += (
                            "<b>🎉 Отлично!</b>\n\n"
                            "Вы успешно зарегистрированы как <b>📢 Заказчик</b>.\n"
                            "Теперь вы можете <i>разместить новый проект</i>.\n\n"
                            "Если что-то пойдёт не так — всегда можно изменить данные в настройках."
                        )
                        
                    else:
                        message += (
                            "<b>🎉 Отлично!</b>\n\n"
                            "Вы успешно зарегистрированы как <b>🧑‍💻 Исполнитель</b>.\n"
                            "Теперь вы можете <i>искать интересные проекты</i>.\n\n"
                            "Если что-то пойдёт не так — всегда можно изменить данные в настройках."
                        )
                
                    bot.send_message(
                        msg.chat.id , 
                        message , 
                        parse_mode='HTML'
                    )
                    
                    support.show_home(bot=bot , user_id=msg.from_user.id)
                    
        except Exception as e:
            logger.error(f'Error in process_fullname_selection:{e}')

