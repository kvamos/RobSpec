import sqlite3
import logging
from typing import Optional
from . import db_general as g

logger = logging.getLogger(__name__)



def get_employer_data(employer_id: int) -> dict:
    """Возвращает данные работодателя и его проекты"""
    
    default_data = {
        'full_name': 'Неизвестно',
        'rating': 5,
        'projects': []
    }
    
    try:
        with g.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Получаем основные данные пользователя
            cursor.execute("""
                SELECT full_name, rating , balance
                FROM users 
                WHERE user_id = ?
            """, (employer_id,))
            
            user_row = cursor.fetchone()
            if not user_row:
                return default_data
                
            user_data = dict(user_row)
            user_data['projects'] = []
            
            # Получаем проекты работодателя
            cursor.execute("""
                SELECT project_id, title, status, deadline
                FROM projects
                WHERE employer_id = ? and status != 'canceled'
                ORDER BY editing_at DESC
                LIMIT 3
            """, (employer_id,))
            
            user_data['projects'] = [dict(row) for row in cursor.fetchall()]
            return user_data
            
    except sqlite3.Error as e:
        logger.error(f"Error in get_employer_data: {e}")



def create_project(employer_id: int, title: str, description: Optional[str], deadline: str, price: float) -> int:
    """Создает новый проект и возвращает его ID"""
    
    try:
        if not title or len(title.strip()) < 3:
            raise ValueError("Название проекта слишком короткое")
            
        if not deadline:
            raise ValueError("Не указан срок выполнения")
            
        if price <= 0:
            raise ValueError("Цена должна быть положительной")
            
        with g.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO projects (
                    employer_id,
                    title,
                    description,
                    status,
                    deadline,
                    price
                ) VALUES (?, ?, ?, 'active', ?, ?)
            """, (
                employer_id,
                title.strip(),
                description.strip() if description else None,
                deadline,
                round(float(price), 2)
            ))
            conn.commit()
            return cursor.lastrowid
            
    except sqlite3.Error as e:
        logger.error(f"Error in creat_project: {e}")
        return None
    except ValueError as e:
        logger.error(f"Validation error when creating a project {e}")
        return None



def get_project_ids_employer(employer_id: int) -> list[int]:
    """Возвращает список ID проектов заказчика."""
    
    try:
        with g.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT project_id FROM projects WHERE status != 'canceled' and employer_id = ?",
                (employer_id,)
            )
            return [row[0] for row in cursor.fetchall()]

    except sqlite3.Error as e:
        logger.error(f"Error in get_projects_id_employer: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_projects_ids_employer: {e}")
        return None



def get_employer_application_ids(employer_id: int) -> list[int]:
    """Возвращает список ID всех откликов заказчика"""
    
    try:
        with g.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT a.app_id FROM applications a "
                "JOIN projects p ON a.project_id = p.project_id "
                "WHERE p.employer_id = ?",
                (employer_id,)
            )
            return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error in get_employer_application_ids: {e}")
        return None



def get_project_applications_except(project_id: int, app_id: int) -> list[int]:
    """Возвращает все ID откликов на указанный проект, кроме заданного отклика"""
    
    try:
        with g.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT app_id FROM applications WHERE project_id = ? AND app_id != ?",
                (project_id, app_id)
            )
            return [row[0] for row in cursor.fetchall()]
        
    except sqlite3.Error as e:
        print(f"Error in get_project_applications_except: {e}")
        return None



def get_approved_application_id(project_id: int) -> Optional[int]:
    """Возвращает ID подтверждённого отклика для указанного проекта"""
    
    try:
        with g.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT app_id FROM applications WHERE project_id = ? AND status = 'approved' LIMIT 1",
                (project_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
        
    except sqlite3.Error as e:
        print(f"Error in get_approved_application_id: {e}")
        return None