from .h_general import *
from .h_employer import *
from .h_student import *

__all__ = ['h_general' , 'h_employer' , 'h_student']

def register_all_handlers(bot):
    """Регистрирует все обработчики бота"""
    register_general_handlers(bot)
    register_employer_handlers(bot)
    register_student_handlers(bot)

