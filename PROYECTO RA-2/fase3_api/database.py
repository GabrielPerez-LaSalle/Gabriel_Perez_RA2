"""
Configuración de la base de datos
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator
from config import settings

@contextmanager
def get_db_connection() -> Generator:
    """
    Context manager para conexiones a la base de datos
    
    Yields:
        Connection: Conexión a PostgreSQL con cursor tipo diccionario
    """
    conn = None
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            port=settings.DB_PORT,
            sslmode=settings.DB_SSLMODE,
            cursor_factory=RealDictCursor
        )
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def execute_query(query: str, params: tuple = None) -> list:
    """
    Ejecuta una query SELECT y retorna los resultados
    
    Args:
        query: SQL query a ejecutar
        params: Parámetros para la query
        
    Returns:
        Lista de diccionarios con los resultados
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()

def execute_single_query(query: str, params: tuple = None) -> dict:
    """
    Ejecuta una query SELECT y retorna un solo resultado
    
    Args:
        query: SQL query a ejecutar
        params: Parámetros para la query
        
    Returns:
        Diccionario con el resultado o None
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()

def test_connection() -> bool:
    """
    Prueba la conexión a la base de datos
    
    Returns:
        True si la conexión es exitosa
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False
