"""
Configuración para la extracción de datos de Polymarket API
Fase 1: Recolección de datos desde los endpoints de Polymarket
"""

# URLs base de la API de Polymarket
BASE_URL = "https://gamma-api.polymarket.com"

# Endpoints disponibles
ENDPOINTS = {
    "tags": f"{BASE_URL}/tags",
    "events": f"{BASE_URL}/events",
    "series": f"{BASE_URL}/series",
    "markets": f"{BASE_URL}/markets"
}

# Configuración de extracción
EXTRACTION_CONFIG = {
    "limit": 1000,  # Límite de registros por petición (aumentado para máxima extracción)
    "offset": 0,   # Offset inicial
    "max_records": 0  # Máximo de registros a extraer por endpoint (0 = sin límite, extrae TODOS los datos)
}

# Rutas de archivos
DATA_DIR = "data"
LOGS_DIR = "logs"
DELTA_DIR = "delta_lake"  # Directorio para tablas Delta Lake

# Configuración de archivos JSON (legacy)
JSON_CONFIG = {
    "indent": 4,
    "ensure_ascii": False
}

# Configuración Delta Lake
DELTA_CONFIG = {
    "storage_format": "parquet",
    "compression": "snappy",
    "enable_schema_evolution": True,
    "enable_versioning": True
}

# Timeout para las peticiones HTTP (en segundos)
REQUEST_TIMEOUT = 30

# Headers para las peticiones
HEADERS = {
    "User-Agent": "Polymarket-Data-Extractor/1.0",
    "Accept": "application/json"
}

# Verificación SSL (True = verificar, False = no verificar)
VERIFY_SSL = False

# Configuración de reintentos
RETRY_CONFIG = {
    "max_retries": 5,
    "retry_delay": 2,  # segundos entre reintentos
    "backoff_factor": 1.5  # multiplicador para el delay en cada reintento
}
