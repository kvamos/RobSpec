from telebot import types , TeleBot
import DataBase as db
import keyboards
from datetime import datetime , timedelta
import support
from decorator import *



def home_employer(bot: TeleBot, user_id: int):
    """Отображает домашнюю страницу заказчика"""
    try:
        # Получаем данные работодателя
        employer_data = db.get_employer_data(user_id)
        
        # Проверяем и подготавливаем данные
        if not employer_data or 'projects' not in employer_data:
            raise ValueError("Некорректные данные работодателя")
            
        active_projects = employer_data['projects'] or []  # Гарантируем, что это список
        
        # Формируем сообщение
        message = (
            "<b>💼 Ваш профиль заказчика</b>\n\n"
            f"💰 <b>Баланс:</b> <code>{employer_data.get('balance', 0)}₽</code>\n"
            f"⭐ <b>Рейтинг:</b> <code>{employer_data.get('rating', 0)}/5.0</code>\n"
            f"📁 <b>Ваши проекты:</b> <code>{len(active_projects)}</code>\n\n"
        )
        
        if not active_projects:
            message += 'У вас пока нет опубликованных проектов'
        else:
            message += '<b>📌 Последние проекты:</b>\n'
            for i, project in enumerate(active_projects[:3], 1):
                message += f'{i}. {project["title"]}\n'
                
        # Отправляем сообщение
        bot.send_message(
            user_id, 
            message, 
            parse_mode="HTML", 
            reply_markup=keyboards.home_employer_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in home_employer for user {user_id}: {e}")
        bot.send_message(
            user_id,
            "⚠ Произошла ошибка при загрузке профиля. Попробуйте позже."
        )




def register_employer_handlers(bot: TeleBot):
    
    
    @bot.message_handler(func=lambda m: m.text == "➕ Новый проект")
    @employer_only(bot , lambda msg: msg)
    def start_create_project(msg):
        try:
            bot.delete_state(msg.from_user.id , msg.chat.id)
            bot.set_state(msg.from_user.id , "project_creation" , msg.chat.id)
            
            message = (
                "<b>📝 Давайте создадим новый проект!</b>\n\n"
                "<b>Шаг 1 из 4</b>\n"
                "Введите <b>название проекта</b>.\n\n"
                "Примеры:\n"
                "▪️ Сайт-портфолио на Tilda\n"
                "▪️ Чат-бот для Telegram\n"
                "▪️ 3D-модель персонажа для игры\n\n"
                "Для отмены /cancel"
            )
            
            bot.send_message(
                msg.chat.id ,
                message , 
                parse_mode= 'HTML' , 
                reply_markup=types.ReplyKeyboardRemove()
            )
            
            bot.register_next_step_handler(msg , process_project_title)

        except Exception as e:
            logger.error(f'Error in start_create_project: {e}')
    
    
    def process_project_title(msg):
        try:
            if msg.text == '/cancel':
                support.cancel_create_project(bot , msg.chat.id)
                home_employer(bot , msg.from_user.id)
                
            else:
                bot.add_data(msg.from_user.id , msg.chat.id , title = msg.text)
                
                message = (
                    "<b>📄 Шаг 2 из 4</b>\n"
                    "Опишите <b>подробности проекта</b>.\n\n"
                    "Что нужно сделать, какие требования, есть ли примеры?\n\n"
                    "<i>Пример:</i>\n"
                    "Нужен Telegram-бот для приёма заявок. Пользователь вводит имя и номер, а данные приходят в мой личный аккаунт.\n\n"
                    "Для отмены /cancel"
                )
                
                bot.send_message(
                    msg.chat.id , 
                    message , 
                    parse_mode='HTML'
                )
                
                bot.register_next_step_handler(msg , process_project_description)
            
        except Exception as e:
            logger.error(f'Error in process_project_title: {e}')


    def process_project_description(msg):
        try:
            if msg.text == '/cancel':
                support.cancel_create_project(bot , msg.chat.id)
                home_employer(bot , msg.from_user.id)

            else:
                bot.add_data(msg.from_user.id , msg.chat.id , description = msg.text)
                
                message = (
                    "<b>⏳ Шаг 3 из 4</b>\n"
                    "Укажите <b>срок, до которого проект должен быть завершён(минимум через неделю)</b>.\n"
                    "формат: <code>ДД.ММ.ГГГГ</code>\n\n"
                    "Для отмены /cancel"
                )
                
                bot.send_message(
                    msg.chat.id , 
                    message , 
                    parse_mode='HTML'
                )
                bot.register_next_step_handler(msg, process_project_deadline)
        
        except Exception as e:
            logger.error(f'Error in process_project_description: {e}')


    def process_project_deadline(msg):
        try:
            if msg.text == '/cancel':
                support.cancel_create_project(bot , msg.chat.id)
                home_employer(bot , msg.from_user.id)

            else:
                deadline = datetime.strptime(msg.text, "%d.%m.%Y").date()
                
                if deadline < (datetime.now().date() + timedelta(weeks=1)):
                    bot.send_message(
                        msg.chat.id , 
                        'указаная дата меньше чем через неделю' 
                    )
                    return bot.register_next_step_handler(msg , process_project_deadline)

                bot.add_data(msg.from_user.id, msg.chat.id, deadline=deadline)
                
                message = (
                    "<b>💰 Шаг 4 из 4</b>\n"
                    "Сколько вы готовы заплатить за выполнение проекта?\n\n"
                    "<i>Пример:</i>\n"
                    "▪️ 1500\n"
                    "▪️ 3000₽\n\n"
                    "Для отмены /cancel"
                )
                
                bot.send_message(
                    msg.chat.id , 
                    message , 
                    parse_mode='HTML'
                )
                bot.register_next_step_handler(msg, finalize_project_creation)
        
        except ValueError:
            bot.send_message(msg.chat.id, "❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ")
            bot.register_next_step_handler(msg, process_project_deadline)
        
        except Exception as e:
            logger.error(f'Error in process_project_deadline: {e}')


    def finalize_project_creation(msg):
        try:
            if msg.text == '/cancel':
                support.cancel_create_project(bot , msg.chat.id)
                home_employer(bot , msg.from_user.id)

            else:
                price = float(''.join(char for char in (msg.text) if char.isdigit()))
                
                if price <= 0:
                    bot.send_message(msg.chat.id, "❌ Цена должна быть больше 0")
                    return bot.register_next_step_handler(msg, finalize_project_creation)
                
                with bot.retrieve_data(msg.from_user.id, msg.chat.id) as data:
                    project_id = db.create_project(
                        employer_id=msg.from_user.id,
                        title=data['title'],
                        description=data['description'],
                        deadline=data['deadline'],
                        price=price
                    )
            
                if project_id:
                    bot.send_message(
                        msg.chat.id,
                        f"✅ Проект «{data['title']}» успешно создан!",
                        reply_markup=keyboards.home_employer_keyboard()
                    )
                    logger.info(f'user {msg.from_user.id} created the project {project_id}')
                else:
                    bot.send_message(
                        msg.chat.id,
                        "❌ Не удалось создать проект. Попробуйте позже.",
                        reply_markup=keyboards.home_employer_keyboard()
                    )
                    logger.info(f"user {msg.from_user.id} couldn't create the project")
                
        except Exception as e:
            logger.error(f'Error finalize_project_creation: {e}')
        
        
        
        
        
    @bot.message_handler(func=lambda m: m.text == "📂 Мои проекты")
    @employer_only(bot , lambda msg: msg)
    def projects_employer(msg):
        try:
            employer_id = int(msg.from_user.id)
            project_ids = db.get_project_ids_employer(employer_id=employer_id)
            
            if not project_ids:
                bot.send_message(msg.chat.id, "📭 У вас пока нет проектов.")
                return
            
             # Показываем первый проект
            support.show_project_employer(bot , msg.from_user.id , project_ids[0] , 0 , msg.message_id)
            
        except Exception as e:
            logger.error(f'Error in projects_employer: {e}')


    @bot.callback_query_handler(func=lambda call: call.data.startswith(('employer_project_prev_' , 'employer_project_next_')))
    @employer_only(bot , lambda msg: msg)
    def handle_navigation(call):
        try:
            _ , _ , action , project_id , index = call.data.split('_')
            project_id , new_index = int(project_id) , int(index)

            employer_id = db.get_project_info(project_id , 'employer_id')
            all_projects = db.get_project_ids_employer(employer_id)
            if not all_projects:
                bot.answer_callback_query(call.id , 'У вас нет проектов')
                return

            new_project_id = all_projects[new_index]

            support.show_project_employer(
                bot , 
                employer_id , 
                new_project_id , 
                new_index , 
                call.message.message_id
            )

        except Exception as e:
            logger.error(f'Error in handle_navigation: {e}')
    
    
    @bot.callback_query_handler(func=lambda call: call.data in ('employer_project_boundary_first', 'employer_project_boundary_last'))
    @employer_only(bot , lambda msg: msg)
    def handle_boundary(call):
        if call.data == 'employer_project_boundary_first':
            bot.answer_callback_query(call.id, "Это крайний проект", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Это крайний проект", show_alert=True)
    
    
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('employer_project_cancel_'))
    @employer_only(bot , lambda msg: msg)
    def handle_project_application(call):
        try:
            project_id = int(call.data.split('_')[3])
            db.update_project_status(project_id=project_id , new_status='canceled')
            bot.answer_callback_query(call.id, "проект отменён" , show_alert=True)
        except Exception as e:
            bot.answer_callback_query(call.id, "Ошибка отклика")
            print(f"Error in handle_project_application: {e}")