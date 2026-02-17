# 🎓 PROYECTO RA-2: Data Engineering Pipeline Completo

## Polymarket Data Warehouse - 3 Fases Completadas

**Autor**: Gabriel  
**Fecha**: Febrero 2026  
**Curso**: Data Engineering - La Salle  

---

## 📊 Resumen del Proyecto

Este proyecto implementa un **pipeline completo de datos** desde la extracción de APIs hasta la exposición mediante API REST, siguiendo las mejores prácticas de Data Engineering.

### Fuente de Datos
**Polymarket API** - Plataforma de mercados de predicción descentralizada
- Markets (Mercados de predicción)
- Events (Eventos que contienen mercados)
- Series (Series de eventos recurrentes)
- Tags (Categorización jerárquica)

---

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                     FASE 1: EXTRACCIÓN                      │
│  Polymarket API → Delta Lake (Bronze/Silver)                │
│  - Extracción incremental con rate limiting                 │
│  - Validación y limpieza de datos                           │
│  - Almacenamiento en formato Delta (ACID)                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    FASE 2: WAREHOUSE                         │
│  Delta Lake → NeonDB PostgreSQL (Gold)                       │
│  - ETL con transformaciones avanzadas                        │
│  - Modelo dimensional (Star Schema)                          │
│  - Optimización con índices y particiones                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    FASE 3: API REST                          │
│  NeonDB → FastAPI → Consumidores externos                    │
│  - 10+ endpoints especializados                              │
│  - Documentación automática (Swagger/ReDoc)                  │
│  - Validación con Pydantic                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del Proyecto

```
PROYECTO RA-2/
│
├── fase1_extraccion/              # FASE 1: Extracción de datos
│   ├── main.py                    # Pipeline principal
│   ├── extract_*.py               # Scripts de extracción por entidad
│   ├── config.py                  # Configuración API
│   ├── delta_utils.py             # Utilidades Delta Lake
│   ├── requirements.txt           # Dependencias
│   │
│   ├── data/                      # Datos extraídos
│   │   └── exported/              # Exports CSV
│   │
│   ├── delta_lake/                # Delta Lake storage
│   │   ├── events/
│   │   ├── markets/
│   │   ├── series/
│   │   └── tags/
│   │
│   ├── fase2_warehouse/           # FASE 2: Data Warehouse
│   │   ├── etl_warehouse.py       # ETL completo
│   │   ├── schema_ddl.sql         # DDL del warehouse
│   │   ├── neondb_config.py       # Configuración NeonDB
│   │   ├── create_schema.py       # Creación de tablas
│   │   └── validate_warehouse.py # Validación de datos
│   │
│   └── fase3_api/                 # FASE 3: API REST ⭐ NUEVO
│       ├── main.py                # Aplicación FastAPI
│       ├── config.py              # Settings
│       ├── database.py            # Conexión DB
│       ├── models.py              # Modelos Pydantic
│       ├── requirements.txt       # Dependencias
│       ├── run_api.bat            # Script de ejecución
│       │
│       ├── routers/               # Endpoints modulares
│       │   ├── markets.py         # Endpoints de mercados
│       │   ├── events.py          # Endpoints de eventos
│       │   ├── series.py          # Endpoints de series
│       │   ├── tags.py            # Endpoints de tags
│       │   └── analytics.py       # Endpoints de análisis
│       │
│       ├── README.md              # Documentación completa
│       └── ENDPOINTS_DOCUMENTATION.md  # Docs para GitHub compartido
│
└── README.md                      # Este archivo
```

---

## 🚀 FASE 1: Extracción de Datos

### Características
- ✅ Extracción incremental desde Polymarket API
- ✅ Rate limiting y manejo de errores
- ✅ Almacenamiento en Delta Lake (ACID)
- ✅ Validación de esquemas
- ✅ Exports a CSV

### Tecnologías
- Python 3.10+
- Delta Lake
- Pandas
- Requests

### Ejecución
```bash
cd fase1_extraccion
python main.py
```

### Resultados
- **4 tablas Delta Lake**: events, markets, series, tags
- **Datos exportados**: CSV en `data/exported/`
- **Logs detallados**: Tracking de extracciones

---

## 🏛️ FASE 2: Data Warehouse

### Características
- ✅ Modelo dimensional (Star Schema)
- ✅ Tablas de dimensiones con SCD Type 2
- ✅ Tabla de hechos desnormalizada
- ✅ Índices optimizados para consultas analíticas
- ✅ NeonDB PostgreSQL (Serverless)

### Esquema del Warehouse

```
Dimensiones:
├── dim_market       # Mercados de predicción
├── dim_event        # Eventos
├── dim_series       # Series recurrentes
├── dim_tag          # Tags jerárquicos
└── dim_time         # Dimensión de tiempo

Hechos:
└── fact_market_metrics  # Métricas (volumen, liquidez, precios)

Puentes:
└── bridge_market_tag    # Relación many-to-many
```

### Tecnologías
- PostgreSQL (NeonDB)
- psycopg2
- Python ETL

### Ejecución
```bash
cd fase1_extraccion/fase2_warehouse
python create_schema.py      # Crear tablas
python etl_warehouse.py      # Ejecutar ETL
python validate_warehouse.py # Validar datos
```

### Métricas del Warehouse
- **Tablas**: 7 (5 dimensiones + 1 hechos + 1 puente)
- **Índices**: 30+ para optimización
- **Registros**: Miles de mercados y eventos
- **Queries**: Optimizadas para analytics

---

## 🌐 FASE 3: API REST (NUEVO)

### Características
- ✅ **10+ endpoints** especializados
- ✅ Documentación automática (Swagger UI + ReDoc)
- ✅ Validación de datos con Pydantic
- ✅ CORS habilitado
- ✅ Paginación y filtros avanzados
- ✅ Health checks

### Endpoints Principales

| Endpoint | Descripción | Parámetros |
|----------|-------------|------------|
| `GET /markets/top-volume` | Top mercados por volumen | limit, category |
| `GET /markets/closing-soon` | Mercados próximos a cerrar | hours, limit |
| `GET /series/{id}/probability` | Evolución de probabilidades | days |
| `GET /tags/search` | Buscar tags | name, limit |
| `GET /events/closing-soon/list` | Eventos próximos a cerrar | hours, limit |
| `GET /analytics/category-stats` | Estadísticas por categoría | limit |
| `GET /analytics/volume-trends` | Tendencias de volumen | days, category |
| `GET /analytics/trending-markets` | Mercados trending | limit |

### Tecnologías
- FastAPI 0.109.0
- Uvicorn (ASGI server)
- Pydantic 2.5.3
- psycopg2-binary

### Ejecución

**Opción 1: Script automático**
```bash
cd fase1_extraccion/fase3_api
run_api.bat
```

**Opción 2: Manual**
```bash
cd fase1_extraccion/fase3_api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### URLs de Acceso
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Ejemplo de Uso

**Python**:
```python
import requests

# Top 5 mercados por volumen
response = requests.get('http://localhost:8000/markets/top-volume?limit=5')
markets = response.json()

for market in markets:
    print(f"{market['question']}: ${market['volume']:,.2f}")
```

**cURL**:
```bash
# Mercados que cierran en 24 horas
curl "http://localhost:8000/markets/closing-soon?hours=24"

# Estadísticas por categoría
curl "http://localhost:8000/analytics/category-stats?limit=5"
```

---

## 📈 Casos de Uso

### 1. Trading Dashboard
```python
# Obtener mercados trending
GET /analytics/trending-markets?limit=10

# Mercados próximos a cerrar
GET /markets/closing-soon?hours=24

# Estadísticas por categoría
GET /analytics/category-stats
```

### 2. Análisis de Tendencias
```python
# Evolución de probabilidades en series
GET /series/nba-playoffs-2026/probability?days=30

# Tendencias de volumen
GET /analytics/volume-trends?days=7&category=Sports
```

### 3. Búsqueda y Filtrado
```python
# Buscar mercados
GET /markets/search/?query=bitcoin

# Mercados por tag
GET /tags/crypto-bitcoin/markets?active_only=true
```

---

## 🎯 Objetivos Cumplidos

### Fase 1 ✅
- [x] Extracción de 4 endpoints de Polymarket API
- [x] Almacenamiento en Delta Lake
- [x] Validación de datos
- [x] Exports a CSV

### Fase 2 ✅
- [x] Diseño de modelo dimensional
- [x] Creación de Data Warehouse en NeonDB
- [x] ETL completo con transformaciones
- [x] Validación de integridad

### Fase 3 ✅
- [x] API REST con FastAPI
- [x] 10+ endpoints especializados
- [x] Documentación automática
- [x] Validación de datos
- [x] Health checks
- [x] Documentación para GitHub compartido

---

## 📚 Documentación

### Fase 1
- `README.md` en `fase1_extraccion/`
- `API_ENDPOINTS_CHEATSHEET.md`

### Fase 2
- `README.md` en `fase2_warehouse/`
- `schema_ddl.sql` (DDL completo)
- `consultas_analiticas.sql` (Ejemplos de queries)

### Fase 3
- `README.md` en `fase3_api/` (Documentación completa)
- `ENDPOINTS_DOCUMENTATION.md` (Para GitHub compartido)
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🔧 Requisitos del Sistema

### Software
- Python 3.10 o superior
- PostgreSQL (NeonDB) - Cuenta gratuita
- Git

### Dependencias Python (por fase)

**Fase 1**:
```
delta-spark
pandas
requests
python-dotenv
```

**Fase 2**:
```
psycopg2-binary
pandas
python-dotenv
```

**Fase 3**:
```
fastapi
uvicorn[standard]
pydantic
psycopg2-binary
python-dotenv
```

---

## 🚀 Quick Start - Ejecutar Todo el Pipeline

### 1. Extracción (Fase 1)
```bash
cd fase1_extraccion
pip install -r requirements.txt
python main.py
```

### 2. Warehouse (Fase 2)
```bash
cd fase2_warehouse
pip install -r requirements.txt
python create_schema.py
python etl_warehouse.py
```

### 3. API (Fase 3)
```bash
cd fase3_api
pip install -r requirements.txt
python main.py
```

Visita http://localhost:8000/docs para explorar la API

---

## 📊 Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Líneas de código | ~3,500+ |
| Archivos Python | 25+ |
| Endpoints API | 20+ |
| Tablas DB | 7 |
| Índices DB | 30+ |
| Modelos Pydantic | 20+ |
| Documentación (MD) | 6 archivos |

---

## 🌟 Características Destacadas

### Arquitectura
- ✅ **Separación por capas**: Bronze/Silver → Gold → API
- ✅ **Modelo dimensional**: Star Schema optimizado
- ✅ **ACID compliance**: Delta Lake + PostgreSQL

### Código
- ✅ **Modular y reutilizable**
- ✅ **Bien documentado**
- ✅ **Manejo de errores robusto**
- ✅ **Type hints en Python**

### API
- ✅ **RESTful best practices**
- ✅ **Documentación automática**
- ✅ **Validación de datos**
- ✅ **Queries optimizadas**

---

## 🎓 Aprendizajes y Tecnologías

### Data Engineering
- Pipeline ETL completo
- Data Lake (Delta Lake)
- Data Warehouse (Dimensional Modeling)
- API Design

### Tecnologías
- Python (Pandas, FastAPI, Pydantic)
- Delta Lake
- PostgreSQL (NeonDB)
- REST APIs
- Git

### Best Practices
- Clean Code
- Documentation
- Error Handling
- Testing
- Version Control

---

## 📞 Contacto y Entrega

**Estudiante**: Gabriel  
**Proyecto**: RA-2 Data Engineering  

### Repositorios
- **Individual**: [Tu repositorio GitHub individual]
- **Compartido (Clase)**: https://github.com/lasalle-ai/apis

### Entregables
1. ✅ Código completo del pipeline (3 fases)
2. ✅ Documentación de endpoints para GitHub compartido
3. ✅ README completo con instrucciones
4. ✅ Scripts de ejecución automatizados

---

## 🎉 Conclusión

Este proyecto demuestra un **pipeline completo de Data Engineering**, desde la extracción de datos de APIs externas hasta su exposición mediante una API REST profesional, pasando por un Data Warehouse optimizado para analytics.

La arquitectura en 3 fases permite:
- **Escalabilidad**: Cada fase puede escalar independientemente
- **Mantenibilidad**: Código modular y bien documentado
- **Reutilización**: Componentes reutilizables en otros proyectos
- **Producción**: Listo para deployment con ajustes mínimos

---

**Fecha de Finalización**: Febrero 17, 2026  
**Versión**: 1.0.0  
**Estado**: ✅ Completado
