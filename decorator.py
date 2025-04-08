from telebot import TeleBot
from functools import wraps
import logging
import DataBase as db



logger = logging.getLogger(__name__)

def employer_only(bot, message_or_getter):
    """
    Декоратор для проверки прав работодателя.
    Поддерживает:
        - @employer_only(bot, message)  # Прямая передача message
        - @employer_only(bot, lambda msg: msg)  # Ленивое получение message
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Получаем message: либо напрямую, либо через getter (lambda)
            if callable(message_or_getter):
                # Если передан лямбда-геттер (lambda msg: msg)
                message = message_or_getter(*args, **kwargs)
            else:
                # Если передано сообщение напрямую
                message = message_or_getter

            # Проверяем, является ли пользователь работодателем
            if db.get_user_info(message.from_user.id, 'role') != 'employer':
                bot.send_message(message.chat.id, "❌ Доступ только для работодателей!")
                return

            return func(*args, **kwargs)  # Вызываем исходную функцию
        return wrapper
    return decorator


def student_only(func):
    @wraps(func)
    def wrapper(bot: TeleBot, message, *args, **kwargs):
        try:
            if db.get_user_info(message.from_user.id, 'role') != 'students':
                bot.send_message(message.chat.id, "❌ Доступ только для исполнителей")
                logger.warning(f"Unauthorized access attempt by {message.from_user.id}")
                return
            return func(bot, message, *args, **kwargs)
        except Exception as e:
            logger.error(f"Access check failed: {e}", exc_info=True)
            raise
    return wrapper