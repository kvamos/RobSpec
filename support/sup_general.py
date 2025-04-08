from telebot import types
from telebot import TeleBot
import logging
import DataBase as db
import handlers as h
import keyboards

logger = logging.getLogger(__name__)



def show_home(bot: TeleBot, user_id: int):
    try:
        # Получаем роль пользователя с проверкой
        role = db.get_user_info(user_id=user_id, column='role')
        if not role:
            raise ValueError(f"Role not found for user {user_id}")
        
        # Проверяем тип роли (на всякий случай)
        if not isinstance(role, str):
            role = str(role).lower()
        
        # Выбираем соответствующее меню
        if role == 'employer':
            h.home_employer(bot=bot, user_id=user_id)
        elif role == 'student':
            h.home_student(bot=bot, user_id=user_id)
        else:
            logger.warning(f"Unknown role '{role}' for user {user_id}")
            bot.send_message(
                user_id,
                "⚠ Ваш профиль требует обновления. Пожалуйста, выберите роль заново.",
                reply_markup=keyboards.role_keyboard()
            )
    
    except Exception as bot_error:
        logger.error(f"Failed to show home menu for user {user_id}: {str(bot_error)}", exc_info=True)
        try:
            bot.send_message(
                user_id,
                "⚠ Произошла ошибка при загрузке главного меню. Пожалуйста, попробуйте позже."
            )
        except Exception as e:
            logger.critical(f"Failed to send error message to user {user_id}: {str(e)}")

