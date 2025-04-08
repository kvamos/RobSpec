import sqlite3
import logging
from typing import Dict
from . import db_general as g

logger = logging.getLogger(__name__)



def get_student_data(user_id: int) -> Dict:
    """Возвращает все данные студента"""
    
    try:
        with g.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    full_name, 
                    rating,
                    balance, 
                    (SELECT COUNT(*) FROM applications 
                     WHERE student_id = ? AND status = 'approved') AS active_tasks_count
                FROM users 
                WHERE user_id = ?
            """, (user_id, user_id))
            
            result = cursor.fetchone()
            return dict(result) if result else None
        
    except sqlite3.Error as e:
        logger.error(f"Error in get_student_data: {e}")
        return None



def get_project_ids_student() -> list[int]:
    """Получает список ID всех доступных проектов (исключая отменённые)"""
    
    try:
        with g.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT project_id
                FROM projects
                WHERE status IN ('active', 'in_progress', 'wait', 'completed')
                AND status != 'canceled' 
                ORDER BY deadline DESC
            """)
            
            return [row[0] for row in cursor.fetchall()]

    except sqlite3.Error as e:
        print(f"Error in get_project_ids: {e}")
        return None



def create_application(project_id: int, student_id: int) -> dict:
    """Создает новый отклик на проект"""
    
    result = {
        'success': False,
        'message': '',
        'application_id': None,
        'employer_info': {
            'employer_id': None,
            'username': None
        }
    }
    
    try:
        with g.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Проверяем существование студента
            cursor.execute("SELECT 1 FROM users WHERE user_id = ? AND role = 'student'", (student_id,))
            if not cursor.fetchone():
                result['message'] = 'Студент не найден'
                return result
            
            # 2. Проверяем дубликат отклика
            cursor.execute("""
                SELECT 1 FROM applications 
                WHERE project_id = ? AND student_id = ?
                LIMIT 1
            """, (project_id, student_id))
            
            if cursor.fetchone():
                result['message'] = 'Вы уже откликались на этот проект'
                return result
            
            # 3. Получаем информацию о заказчике и проверяем проект
            cursor.execute("""
                SELECT u.user_id, u.username 
                FROM projects p
                JOIN users u ON p.employer_id = u.user_id
                WHERE p.project_id = ?
            """, (project_id,))
            
            employer_data = cursor.fetchone()
            
            if not employer_data:
                result['message'] = 'Проект не найден'
                return result
                
            employer_id, employer_username = employer_data
            result['employer_info'] = {
                'employer_id': employer_id,
                'username': employer_username
            }

            # 4. Создаем заявку
            cursor.execute("""
                INSERT INTO applications (project_id, student_id, status, applied_at)
                VALUES (?, ?, 'pending', datetime('now'))
            """, (project_id, student_id))
            
            app_id = cursor.lastrowid
            conn.commit()
            
            result.update({
                'success': True,
                'message': 'Ваш отклик успешно отправлен!',
                'application_id': app_id
            })
            
            return result
            
    except sqlite3.Error as e:
        logger.error(f'Error in create_application:{e}')
        return result
    except Exception as e:
        logger.error(f"Unexpected error in create_application: {e}")
        return result



def get_student_active_projects(student_id: int) -> list[int]:
    """Возвращает список ID проектов, которые выполняет студент"""
    
    try:
        with g.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT a.project_id
                FROM applications a
                JOIN projects p ON a.project_id = p.project_id
                WHERE a.student_id = ?
                  AND a.status = 'approved'
                  AND p.status = 'in_progress'
                ORDER BY p.deadline ASC
            """, (student_id,))
            
            return [row[0] for row in cursor.fetchall()]
            
    except sqlite3.Error as e:
        logger.error(f'Error in get_student_active_projects: {e}')
        return None