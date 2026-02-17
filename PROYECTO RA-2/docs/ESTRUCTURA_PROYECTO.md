# Estructura del Proyecto RA-2

## Organización General

El proyecto está organizado en 4 carpetas principales que corresponden a las diferentes fases del desarrollo:

```
PROYECTO RA-2/
├── docs/                          # Documentación del proyecto
│   ├── ESTRUCTURA_PROYECTO.md     # Este archivo
│   ├── INSTRUCCIONES_ENTREGA.md   # Instrucciones de entrega
│   ├── INVENTARIO_PROYECTO.md     # Inventario de componentes
│   └── Proyecto RA2_.pdf          # Documento del proyecto
│
├── fase1_extraccion/              # Fase 1: Extracción y Data Lake
│   ├── config/                    # Archivos de configuración
│   │   └── thunder-collection_polymarket.json
│   ├── data/                      # Datos exportados (CSV)
│   │   └── exported/
│   │       ├── events_*.csv
│   │       ├── markets_*.csv
│   │       ├── series_*.csv
│   │       └── tags_*.csv
│   ├── delta_lake/                # Delta Lake (archivos Parquet)
│   │   ├── events/
│   │   ├── markets/
│   │   ├── series/
│   │   └── tags/
│   ├── docs/                      # Documentación de Fase 1
│   │   ├── API_ENDPOINTS_CHEATSHEET.md
│   │   ├── FASE2_RESUMEN_COMPLETADO.md
│   │   ├── THUNDER_CLIENT_GUIA.md
│   │   └── THUNDER_CLIENT_QUICKSTART.md
│   ├── logs/                      # Archivos de log
│   │   ├── delta_lake_*.log
│   │   └── etl_warehouse_*.log
│   ├── notebooks/                 # Jupyter Notebooks
│   │   └── extraer_datos_delta_lake.ipynb
│   ├── reportes/                  # Reportes de volumetría
│   │   ├── INDICE_REPORTE_VOLUMETRIA_*.txt
│   │   └── volumetria_*.csv
│   ├── scripts/                   # Scripts de Python
│   │   ├── analizar_duplicados.py
│   │   ├── analizar_overflow.py
│   │   ├── check_delta.py
│   │   ├── check_warehouse_status.py
│   │   ├── config.py
│   │   ├── delta_utils.py
│   │   ├── explorar_relaciones.py
│   │   ├── explorar_tags_estructura.py
│   │   ├── explorar_warehouse.py
│   │   ├── extract_events.py
│   │   ├── extract_markets.py
│   │   ├── extract_series.py
│   │   ├── extract_tags.py
│   │   ├── extraer_completo.py
│   │   ├── generar_reporte_volumetria.py
│   │   ├── limpiar_proyecto.py
│   │   ├── main.py
│   │   ├── verificacion_final.py
│   │   └── verificar_estructura_db.py
│   ├── README.md                  # Documentación de Fase 1
│   ├── requirements.txt           # Dependencias Python
│   └── run.bat                    # Script de ejecución
│
├── fase2_warehouse/               # Fase 2: Data Warehouse
│   ├── consultas_analiticas.sql   # Consultas SQL analíticas
│   ├── create_schema.py           # Script de creación de schema
│   ├── etl_carga_completa.py      # ETL completo
│   ├── etl_csv_simple.py          # ETL simple desde CSV
│   ├── etl_warehouse.py           # ETL principal
│   ├── fix_schema_overflow.py     # Corrección de schema
│   ├── neondb_config.py           # Configuración NeonDB
│   ├── README.md                  # Documentación de Fase 2
│   ├── schema_ddl.sql             # DDL del schema
│   └── validate_warehouse.py      # Validación del warehouse
│
├── fase3_api/                     # Fase 3: API REST
│   ├── routers/                   # Routers de FastAPI
│   │   ├── analytics.py
│   │   ├── events.py
│   │   ├── markets.py
│   │   ├── series.py
│   │   └── tags.py
│   ├── .env                       # Variables de entorno (no en git)
│   ├── .env.example               # Ejemplo de variables de entorno
│   ├── config.py                  # Configuración de la API
│   ├── database.py                # Conexión a base de datos
│   ├── ENDPOINTS_DOCUMENTATION.md # Documentación de endpoints
│   ├── FASE3_COMPLETADA.md        # Resumen de completación
│   ├── main.py                    # Aplicación principal FastAPI
│   ├── models.py                  # Modelos Pydantic
│   ├── README.md                  # Documentación de Fase 3
│   ├── requirements.txt           # Dependencias Python
│   ├── run_api.bat                # Script de ejecución
│   ├── test_endpoints.py          # Tests de endpoints
│   ├── test_setup.py              # Configuración de tests
│   └── test_simple.py             # Tests simples
│
├── .gitignore                     # Archivos ignorados por Git
├── estructura_proyecto.txt        # Árbol de estructura
└── README.md                      # README principal del proyecto
```

## Archivos Importantes Mantenidos

### Datos Exportados (CSV)
- `fase1_extraccion/data/exported/*.csv` - Datos exportados desde la API

### Delta Lake (Parquet)
- `fase1_extraccion/delta_lake/*/` - Archivos Parquet del Delta Lake
- Incluye carpetas: events, markets, series, tags

### Logs
- `fase1_extraccion/logs/*.log` - Logs de ejecución de scripts

### Reportes
- `fase1_extraccion/reportes/*.csv` - Reportes de volumetría y análisis
- `fase1_extraccion/reportes/*.txt` - Índices de reportes

## Archivos Eliminados

Los siguientes archivos fueron eliminados durante la limpieza:
- `__pycache__/` - Archivos compilados de Python (en todas las ubicaciones)

## Configuración de Git

El archivo `.gitignore` ha sido actualizado para:
- ✅ Mantener archivos de datos importantes (CSV, Parquet, logs)
- ❌ Ignorar archivos compilados de Python (`__pycache__/`, `*.pyc`)
- ❌ Ignorar entornos virtuales (`venv/`, `env/`)
- ❌ Ignorar archivos de configuración sensibles (`.env`, excepto `.env.example`)
- ❌ Ignorar checkpoints de Jupyter (`.ipynb_checkpoints/`)

## Notas

- Cada fase tiene su propio `README.md` con documentación específica
- Los archivos de configuración están organizados en carpetas dedicadas
- Los scripts están separados de los datos para mejor organización
- La documentación está centralizada en la carpeta `docs/`
