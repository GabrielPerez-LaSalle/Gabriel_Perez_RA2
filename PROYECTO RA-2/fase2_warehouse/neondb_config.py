"""
Configuración de conexión a NeonDB PostgreSQL
Fase 2: Data Warehouse (Capa Gold)
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de NeonDB
NEONDB_CONFIG = {
    # Branch Development
    "development": {
        "host": "ep-purple-sea-aifhrgfm-pooler.c-4.us-east-1.aws.neon.tech",
        "database": "neondb",
        "user": "neondb_owner",
        "password": os.getenv("NEONDB_PASSWORD", "npg_DyquCVg3UvL8"),
        "port": 5432,
        "sslmode": "require",
        "branch_id": "br-solitary-paper-aixy2j6f"
    },
    # Branch Production (cuando esté listo)
    "production": {
        "host": "ep-purple-sea-aifhrgfm-pooler.c-4.us-east-1.aws.neon.tech",
        "database": "neondb",
        "user": "neondb_owner",
        "password": os.getenv("NEONDB_PASSWORD", "npg_DyquCVg3UvL8"),
        "port": 5432,
        "sslmode": "require",
        "branch_id": "br-cold-tooth-aipr1qpz"
    }
}

# Proyecto NeonDB
PROJECT_ID = "rapid-shape-37645142"
PROJECT_NAME = "gabrieldev_RA2"

# Ambiente por defecto
DEFAULT_ENVIRONMENT = "development"

def get_connection_string(environment=DEFAULT_ENVIRONMENT):
    """
    Genera la cadena de conexión para psycopg2
    
    Args:
        environment: 'development' o 'production'
    
    Returns:
        String de conexión para PostgreSQL
    """
    config = NEONDB_CONFIG[environment]
    return (
        f"host={config['host']} "
        f"dbname={config['database']} "
        f"user={config['user']} "
        f"password={config['password']} "
        f"port={config['port']} "
        f"sslmode={config['sslmode']}"
    )

def get_connection_uri(environment=DEFAULT_ENVIRONMENT):
    """
    Genera la URI de conexión (para SQLAlchemy)
    
    Args:
        environment: 'development' o 'production'
    
    Returns:
        URI de conexión PostgreSQL
    """
    config = NEONDB_CONFIG[environment]
    return (
        f"postgresql://{config['user']}:{config['password']}"
        f"@{config['host']}:{config['port']}/{config['database']}"
        f"?sslmode={config['sslmode']}"
    )

def get_config(environment=DEFAULT_ENVIRONMENT):
    """
    Obtiene la configuración completa
    
    Args:
        environment: 'development' o 'production'
    
    Returns:
        Dict con la configuración
    """
    return NEONDB_CONFIG[environment]
