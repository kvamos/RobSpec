from telebot import TeleBot, types
import logging
import DataBase as db
import keyboards

logger = logging.getLogger(__name__)


def show_project_employer(bot: TeleBot, user_id: int, project_id: int, current_index: int, msg_id: int):
    try:
        project = db.get_project_details(project_id)
        employer_id = db.get_project_info(project_id , 'employer_id')

        all_projects_id = db.get_project_ids_employer(employer_id)
        total_projects = len(all_projects_id)

        markup = types.InlineKeyboardMarkup(row_width=3)
        btns = keyboards.projects_navigator_employer(current_index , total_projects , all_projects_id)

        status_info = {
            'active': ('Ищет исполнителя⚪', None),
            'in_progress': ('В процессе выполнения🟢', True),
            'wait': ('Ожидает подтверждение🔵', True),
            'completed': ('Завершён🟡', True)
        }

        status_text, show_executor = status_info.get(project['status'], ('Неизвестный статус', None))
        message = (
            f'название проекта: {project['title']}\n'
            f'статус: {status_text}'
        )

        if show_executor:
            try:
                app_id = db.get_approved_application_id(project_id)
                if app_id:
                    student_id = db.get_application_info(app_id , 'student_id')
                    username = db.get_user_info(student_id , 'username')
                    fullname = db.get_user_info(student_id , 'full_name')
                    msg += f'Исполнитель: {fullname}(@{username})'
            except Exception as e:
                logger.error(f'Error getting executer info:{e}')
        
        message += (
            '\n--------------\n'
            f'Вознаграждение:{project['price']}\n'
            f'Срок выполнения: {project['deadline']}\n\n'
            f'Описание: {project['description']}'
        )

        if project['status'] in ('wait' , 'completed'):
            try:
                app_id = db.get_approved_application_id(project_id)
                if app_id:
                    message_student = db.get_application_info(app_id , 'message')
                    message = f'\n\nРезультат: {message_student}'
            except Exception as e:
                logger.error(f'Error getting result info: {e}')
        
        if project['status'] == 'active':
            btn_activite = types.InlineKeyboardButton(
                'отменить' , 
                callback_data=f'employer_project_cancel_{project_id}_{current_index}'
            )
            markup.row(btns[0] , btn_activite , btns[1])
        
        elif project['status'] == 'wait':
            btn_activite1 = types.InlineKeyboardButton(
                'Подтвердить' , 
                callback_data=f'employer_project_confirmation_{project_id}_{current_index}'
            )
            btn_activite2 = types.InlineKeyboardButton(
                "Отклонить", 
                callback_data=f"employer_project_reject_{project_id}_{current_index}"
            )
            markup.row(btns[0] ,  btns[1] , btn_activite1 , btn_activite2)
        
        elif project['status'] == 'completed':
            btn_activite = types.InlineKeyboardButton(
                "Удалить", 
                callback_data=f"employer_project_remove_{project_id}_{current_index}"
            )
        
        else:
            markup.row(btns[0] , btns[1])
        

        try:
            bot.edit_message_text(
                chat_id = user_id , 
                message_id = msg_id ,
                text = message , 
                reply_markup=markup
            )

        except Exception as edit_erroe:
            new_message = bot.send_message(user_id , message , reply_markup=markup)
            return new_message.message_id

    except Exception as e:
        logger.error(f"Error in show_project_employer: {e}", exc_info=True)