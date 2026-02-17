"""
Configuración de la API
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuración de la aplicación"""
    
    # API Settings
    API_TITLE = "Polymarket Data Warehouse API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = """
    API REST para consultar datos del Data Warehouse de Polymarket.
    
    ## Características
    
    * **Markets**: Consulta de mercados con métricas de volumen, liquidez y precios
    * **Events**: Información de eventos y predicciones
    * **Series**: Series de mercados (NBA, Elections, etc.)
    * **Tags**: Búsqueda y filtrado por tags categorizados
    * **Analytics**: Análisis y tendencias de datos
    
    ## Autor
    Gabriel - Proyecto RA-2
    """
    
    # Database Settings (NeonDB)
    DB_HOST = os.getenv("NEONDB_HOST", "ep-purple-sea-aifhrgfm-pooler.c-4.us-east-1.aws.neon.tech")
    DB_NAME = os.getenv("NEONDB_NAME", "neondb")
    DB_USER = os.getenv("NEONDB_USER", "neondb_owner")
    DB_PASSWORD = os.getenv("NEONDB_PASSWORD", "npg_DyquCVg3UvL8")
    DB_PORT = int(os.getenv("NEONDB_PORT", "5432"))
    DB_SSLMODE = "require"
    
    # API Settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # CORS Settings
    CORS_ORIGINS = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "*"  # En producción, especificar orígenes permitidos
    ]
    
    # Pagination
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
    
    @property
    def database_url(self) -> str:
        """Genera la URL de conexión a PostgreSQL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode={self.DB_SSLMODE}"

settings = Settings()
