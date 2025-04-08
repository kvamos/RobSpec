import time
import logging
from logging.handlers import RotatingFileHandler

from telebot import TeleBot
from telebot.storage import StateMemoryStorage

from config import BOT_TOKEN
from handlers import register_all_handlers
import DataBase


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' ,
        handlers=[
            RotatingFileHandler(
                'bot.log' , 
                maxBytes=5*1024*1024 , 
                backupCount=3
            ) ,
            logging.StreamHandler()
        ]
    )


def main():
    storage = StateMemoryStorage()
    setup_logging()
    logger = logging.getLogger(__name__)
    storage = StateMemoryStorage()
    bot = TeleBot(BOT_TOKEN, state_storage=storage)
    DataBase.init_db()
    register_all_handlers(bot)
    
    while True:
        try:
            logger.info("Starting bot polling...")
            bot.polling(none_stop=True)
        except Exception as e:
            logger.error(f"Error in polling: {e}" , exc_info=True)
            time.sleep(15)


if __name__ == '__main__':
    main()