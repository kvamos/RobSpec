import sqlite3
import logging
from pathlib import Path
from config import DATABASE_PATH
from typing import Union

Path("database").mkdir(exist_ok=True)
logger = logging.getLogger(__name__)


def get_connection():
    """Возвращает созданное подключение к баззе данных"""
    
    return sqlite3.connect(DATABASE_PATH)



def init_db():
    """Инициализирует структуру базы данных"""
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            rating REAL DEFAULT 5,
            balance REAL DEFAULT 0,
            role TEXT CHECK(role IN ('employer', 'student')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
              
        # Таблица проектов
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            deadline DATE,
            price REAL,
            editing_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Таблица заявок
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            app_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER REFERENCES projects(project_id) ON DELETE CASCADE,
            student_id INTEGER REFERENCES users(user_id),
            status TEXT DEFAULT 'pending',
            message TEXT DEFAULT '',
            editing_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()



def user_exists(user_id: int) -> bool:
    """Проверяет, есть ли пользователь в базе данных с таким ID"""
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?" , (user_id , ))
        
        return cursor.fetchone() is not None



def add_user(user_id: int , username: str , full_name: str , role: str , rating: float = 5, balance: float = 0):
    """Добовляет нового пользователя"""
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO 
                users (user_id , username , full_name , rating , balance , role) VALUES (? , ? , ? , ? , ? , ?)
            """ , (user_id , username , full_name , rating , balance , role))
            
            conn.commit()
            return cursor.rowcount > 0
    
    except sqlite3.Error as e:
        logger.error(f"Error in add_user: {e}" , exc_info=True)
        return False



def get_user_info(user_id: int , column: str) -> Union[str , int , float]:
    """Возвращает определённое поле пользователя"""
    
    ALLOWED_COLUMNS = ['username', 'full_name', 'role', 'rating', 'balance', 'created_at']
    if column not in ALLOWED_COLUMNS:
        raise ValueError(f"Недопустимое имя столбца: {column}")
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {column} FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        
    except sqlite3.Error as e:
        logger.error(f'Error in get_user_info: {e}' , exc_info=True)
        return None
    except ValueError as v:
        logger.error(f'Invalid column name') 
        return None  



def get_project_details(project_id: int) -> dict:
    """Возвращает детальную информация о проекте"""
    
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            project_id = int(project_id)
            
            cursor.execute("""
                SELECT 
                    p.*,
                    u.full_name as employer_name
                FROM projects p
                JOIN users u ON p.employer_id = u.user_id
                WHERE p.project_id = ?
                           """ , (project_id , ))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            data = dict(result)
            return data
    except sqlite3.Error as e:
        logger.error(f'Error in get_project_detalis: {e}' , exc_info=True)
        return None



def get_application_details(application_id: int) -> dict:
    """Возвращает детальную информацию об отклике"""
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            application_id = int(application_id)
            
            cursor.execute("""
                SELECT 
                    a.app_id,
                    a.project_id,
                    a.student_id,
                    a.status,
                    a.applied_at,
                    
                    -- Данные студента
                    u.user_id,
                    u.username,
                    u.rating , 
                    u.full_name as student_name,
                    
                    -- Данные проекта
                    p.title as project_title,
                    p.description,
                    p.deadline,
                    p.price,
                    p.employer_id
                FROM applications a
                LEFT JOIN projects p ON a.project_id = p.project_id
                LEFT JOIN users u ON a.student_id = u.user_id
                WHERE a.app_id = ?
            """, (application_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
                
            data = dict(result)

            
            return data
            
    except sqlite3.Error as e:
        logger.error(f"Error in get_application_details: {e}")
        return None
        


def get_application_info(app_id: int , column: str) -> Union[str , int , float]:
    """Возвращает определённое поле заявки"""
    
    ALLOWED_COLUMNS = ['project_id' , 'student_id' , 'status' , 'message' , 'editing_at']
    if column not in ALLOWED_COLUMNS:
        raise ValueError(f"Недопустимое имя столбца: {column}")
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {column} FROM applications WHERE app_id = ?" , (app_id , ))
            
            result = cursor.fetchone()
            return result[0] if result else None
        
    except sqlite3.Error as e:
        logger.error(f'Error in get_application_info: {e}' , exc_info=True)
        return None
    except ValueError as v:
        logger.error(f'Invalid column name')
        return None



def get_project_info(project_id: int , column: str) -> Union[str , int , float]:
    """Возвращет определённое поле проекта"""
    
    ALLOWED_COLUMNS = ['employer_id' , 'title' , 'description' , 'status' , 'deadline' , 'price' , 'editing_at']
    if column not in ALLOWED_COLUMNS:
        raise ValueError(f"Недопустимое имя столбца: {column}")
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {column} FROM projects WHERE project_id = ?", (project_id,))
            
            result = cursor.fetchone()
            return result[0] if result else None
    
    except sqlite3.Error as e:
        logger.error(f'Error in get_project_info: {e}' , exc_info=True)
        return None
    except ValueError as v:
        logger.error(f'Invalid column name')
        return None



def update_project_status(project_id: int, new_status: str) -> bool:
    """Обновляет статус проекта с проверкой существования"""
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT project_id FROM projects WHERE project_id = ? LIMIT 1", 
                (project_id,)
            )
            
            if not cursor.fetchone():
                logger.error(f"Error project with ID {project_id}  not found in the projects table")
                return False
            
            cursor.execute(
                "UPDATE projects SET status = ?, editing_at = CURRENT_TIMESTAMP WHERE project_id = ?",
                (new_status, project_id)
            )
            
            conn.commit()
            updated = cursor.rowcount > 0
            logger.debug(f"Статус проекта {project_id} обновлен на '{new_status}'. Успех: {updated}")
            return updated
            
    except sqlite3.Error as e:
        logger.error(f'Error in update_project_status: {e}' , exc_info=True)
        return False



def update_application_status(app_id: int, new_status: str , new_msg: str = '') -> bool:
    """Обновляет статус заявки с проверкой существования"""
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT project_id FROM applications WHERE app_id = ? LIMIT 1", 
                (app_id,)
            )
            
            if not cursor.fetchone():
                logger.error(f"Error application with ID {app_id} not found in the applications table")
                return False
            
            cursor.execute(
                "UPDATE applications SET status = ?, message = ? , editing_at = CURRENT_TIMESTAMP WHERE app_id = ?",
                (new_status , new_msg , app_id)
            )
            
            conn.commit()
            updated = cursor.rowcount > 0
            print(f"Статус заявки {app_id} обновлен на '{new_status}'. Успех: {updated}")
            return updated
            
    except sqlite3.Error as e:
        logger.error(f'Error in update_application_status: {e}')
        return False



def is_project_executor(project_id: int, user_id: int) -> bool:
    """Проверяет, является ли пользователь исполнителем проекта"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM applications 
                WHERE project_id = ? AND student_id = ? AND status = 'approved'
                LIMIT 1
            """, (project_id, user_id))
            
            return cursor.fetchone() is not None

    except sqlite3.Error as e:
        logger.error(f"Error in is_project_executor: {e}")
        return False