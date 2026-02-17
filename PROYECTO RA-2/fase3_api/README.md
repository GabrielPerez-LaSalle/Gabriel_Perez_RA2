# 🚀 Polymarket Data Warehouse API

**Fase 3: Exposición de Datos**

API REST desarrollada con FastAPI para consultar datos del Data Warehouse de Polymarket. Proporciona acceso programático a mercados de predicción, eventos, series y análisis de datos.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Endpoints](#-endpoints)
  - [Markets](#markets)
  - [Events](#events)
  - [Series](#series)
  - [Tags](#tags)
  - [Analytics](#analytics)
- [Ejemplos de Uso](#-ejemplos-de-uso)
- [Documentación Interactiva](#-documentación-interactiva)
- [Arquitectura](#-arquitectura)

---

## ✨ Características

- ✅ **RESTful API** con FastAPI
- ✅ **Documentación automática** con Swagger UI y ReDoc
- ✅ **Validación de datos** con Pydantic
- ✅ **Consultas optimizadas** a PostgreSQL (NeonDB)
- ✅ **Paginación** en resultados grandes
- ✅ **Filtros avanzados** por categoría, estado, fechas
- ✅ **CORS habilitado** para integración frontend
- ✅ **Health checks** para monitoreo
- ✅ **Analytics y tendencias** de datos

---

## 🛠️ Tecnologías

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.10+ | Lenguaje base |
| FastAPI | 0.109.0 | Framework web |
| Uvicorn | 0.27.0 | ASGI server |
| Pydantic | 2.5.3 | Validación de datos |
| psycopg2 | 2.9.9 | PostgreSQL driver |
| NeonDB | - | Data Warehouse (PostgreSQL) |

---

## 📦 Instalación

### Prerrequisitos

- Python 3.10 o superior
- Acceso a NeonDB (credenciales en `.env`)

### Pasos

1. **Navegar a la carpeta de la API**
   ```bash
   cd fase3_api
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   ```

3. **Activar entorno virtual**
   
   Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

4. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurar variables de entorno**
   ```bash
   # Copiar el archivo de ejemplo
   copy .env.example .env
   
   # Editar .env con tus credenciales
   ```

---

## 🚀 Uso

### Ejecutar la API

**Opción 1: Script automático (Windows)**
```bash
run_api.bat
```

**Opción 2: Comando manual**
```bash
python main.py
```

**Opción 3: Uvicorn directo**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc

---

## 📡 Endpoints

### Root & Health

#### `GET /`
Información general de la API

**Respuesta:**
```json
{
  "message": "Polymarket Data Warehouse API",
  "version": "1.0.0",
  "docs": "/docs",
  "endpoints": {
    "markets": "/markets/",
    "events": "/events/",
    "series": "/series/",
    "tags": "/tags/",
    "analytics": "/analytics/"
  }
}
```

#### `GET /health`
Health check de la API y base de datos

**Respuesta:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "healthy",
  "timestamp": "2026-02-17T10:30:00"
}
```

---

### Markets

#### `GET /markets/top-volume`
Obtiene los mercados con mayor volumen

**Query Parameters:**
- `limit` (int, default=10): Número de resultados (1-100)
- `category` (string, optional): Filtrar por categoría

**Ejemplo:**
```
GET /markets/top-volume?limit=5&category=Sports
```

**Respuesta:**
```json
[
  {
    "market_id": "0x123...",
    "question": "Will Lakers win NBA Championship?",
    "category": "Sports",
    "volume": 1500000.50,
    "volume_24hr": 25000.00,
    "liquidity": 500000.00,
    "outcome_price_yes": 0.65
  }
]
```

---

#### `GET /markets/closing-soon`
Mercados que finalizan próximamente

**Query Parameters:**
- `hours` (int, default=48): Horas hasta el cierre (1-168)
- `limit` (int, default=20): Número de resultados (1-100)

**Ejemplo:**
```
GET /markets/closing-soon?hours=24&limit=10
```

**Respuesta:**
```json
[
  {
    "market_id": "0x123...",
    "question": "Will it rain tomorrow in NYC?",
    "slug": "rain-nyc-tomorrow",
    "category": "Weather",
    "end_date": "2026-02-18T12:00:00",
    "hours_until_close": 14.5,
    "volume": 50000.00,
    "outcome_price_yes": 0.72,
    "active": true
  }
]
```

---

#### `GET /markets/{market_id}`
Detalles completos de un mercado

**Ejemplo:**
```
GET /markets/0x123abc...
```

**Respuesta:**
```json
{
  "market_id": "0x123...",
  "question": "Will BTC reach $100k in 2026?",
  "slug": "btc-100k-2026",
  "description": "Market resolves to Yes if...",
  "category": "Crypto",
  "subcategory": "Bitcoin",
  "market_type": "binary",
  "active": true,
  "closed": false,
  "start_date": "2026-01-01T00:00:00",
  "end_date": "2026-12-31T23:59:59",
  "image": "https://...",
  "outcomes": ["Yes", "No"],
  "metrics": {
    "volume": 2500000.00,
    "volume_24hr": 150000.00,
    "liquidity": 800000.00,
    "outcome_price_yes": 0.45,
    "outcome_price_no": 0.55,
    "last_trade_price": 0.46,
    "spread": 0.02
  }
}
```

---

#### `GET /markets/search/`
Buscar mercados por palabras clave

**Query Parameters:**
- `query` (string, required, min=3): Término de búsqueda
- `limit` (int, default=20): Número de resultados (1-100)

**Ejemplo:**
```
GET /markets/search/?query=election&limit=10
```

---

#### `GET /markets/category/{category}`
Mercados de una categoría específica

**Path Parameters:**
- `category` (string): Nombre de la categoría

**Query Parameters:**
- `active_only` (bool, default=true): Solo mercados activos
- `limit` (int, default=50): Número de resultados
- `offset` (int, default=0): Offset para paginación

**Ejemplo:**
```
GET /markets/category/Sports?active_only=true&limit=20
```

---

### Events

#### `GET /events/{event_id}`
Detalles de un evento específico

**Ejemplo:**
```
GET /events/12345
```

---

#### `GET /events/`
Lista de eventos

**Query Parameters:**
- `category` (string, optional): Filtrar por categoría
- `active_only` (bool, default=true): Solo eventos activos
- `limit` (int, default=50): Número de resultados
- `offset` (int, default=0): Offset para paginación

**Ejemplo:**
```
GET /events/?category=Politics&active_only=true
```

---

#### `GET /events/closing-soon/list`
Eventos que finalizan próximamente

**Query Parameters:**
- `hours` (int, default=48): Horas hasta el cierre
- `limit` (int, default=20): Número de resultados

---

#### `GET /events/featured/list`
Eventos destacados (featured)

**Query Parameters:**
- `limit` (int, default=10): Número de resultados

---

### Series

#### `GET /series/{series_id}`
Detalles de una serie específica

**Ejemplo:**
```
GET /series/nba-playoffs-2026
```

---

#### `GET /series/{series_id}/markets`
Serie con sus mercados asociados

**Query Parameters:**
- `active_only` (bool, default=true): Solo mercados activos
- `limit` (int, default=50): Número de mercados

**Ejemplo:**
```
GET /series/nba-playoffs-2026/markets?limit=20
```

**Respuesta:**
```json
{
  "series_id": "nba-playoffs-2026",
  "title": "NBA Playoffs 2026",
  "slug": "nba-playoffs-2026",
  "description": "All NBA Playoffs markets",
  "series_type": "sports",
  "active": true,
  "total_markets": 45,
  "markets": [
    {
      "market_id": "0x123...",
      "question": "Will Lakers advance to Finals?",
      "slug": "lakers-finals-2026",
      "category": "Sports",
      "active": true
    }
  ]
}
```

---

#### `GET /series/{series_id}/probability`
Evolución de probabilidad promedio de una serie

**Query Parameters:**
- `days` (int, default=30): Días de historial (1-365)

**Ejemplo:**
```
GET /series/nba-playoffs-2026/probability?days=30
```

**Respuesta:**
```json
[
  {
    "date": "2026-02-01",
    "avg_probability_yes": 0.55,
    "market_count": 12
  },
  {
    "date": "2026-02-02",
    "avg_probability_yes": 0.58,
    "market_count": 15
  }
]
```

---

#### `GET /series/`
Lista de series

**Query Parameters:**
- `active_only` (bool, default=true): Solo series activas
- `limit` (int, default=50): Número de resultados

---

### Tags

#### `GET /tags/search`
Buscar tags por nombre

**Query Parameters:**
- `name` (string, required, min=2): Término de búsqueda (ej: 'crypto', 'sports')
- `limit` (int, default=20): Número de resultados

**Ejemplo:**
```
GET /tags/search?name=crypto&limit=10
```

**Respuesta:**
```json
[
  {
    "tag_id": "crypto-bitcoin",
    "label": "Bitcoin",
    "slug": "bitcoin",
    "level": 2
  }
]
```

---

#### `GET /tags/{tag_id}`
Detalles de un tag específico

**Ejemplo:**
```
GET /tags/crypto-bitcoin
```

---

#### `GET /tags/{tag_id}/markets`
Mercados relacionados con un tag

**Query Parameters:**
- `active_only` (bool, default=true): Solo mercados activos
- `limit` (int, default=50): Número de mercados

**Ejemplo:**
```
GET /tags/crypto-bitcoin/markets?active_only=true
```

**Respuesta:**
```json
{
  "tag_id": "crypto-bitcoin",
  "label": "Bitcoin",
  "slug": "bitcoin",
  "level": 2,
  "path": "/crypto/bitcoin",
  "total_markets": 28,
  "markets": [
    {
      "market_id": "0x123...",
      "question": "Will BTC reach $100k?",
      "category": "Crypto",
      "active": true
    }
  ]
}
```

---

#### `GET /tags/`
Lista de tags

**Query Parameters:**
- `level` (int, optional): Filtrar por nivel jerárquico (1-10)
- `limit` (int, default=100): Número de resultados

---

#### `GET /tags/hierarchy/{tag_id}/children`
Tags hijos de un tag específico

**Ejemplo:**
```
GET /tags/hierarchy/sports/children
```

---

### Analytics

#### `GET /analytics/category-stats`
Estadísticas agregadas por categoría

**Query Parameters:**
- `limit` (int, default=20): Número de categorías (1-100)

**Ejemplo:**
```
GET /analytics/category-stats?limit=10
```

**Respuesta:**
```json
[
  {
    "category": "Sports",
    "total_markets": 245,
    "active_markets": 180,
    "total_volume": 5500000.00,
    "avg_volume": 22448.98,
    "total_liquidity": 1200000.00
  }
]
```

---

#### `GET /analytics/volume-trends`
Tendencias de volumen a lo largo del tiempo

**Query Parameters:**
- `days` (int, default=30): Días de historial (1-365)
- `category` (string, optional): Filtrar por categoría

**Ejemplo:**
```
GET /analytics/volume-trends?days=7&category=Crypto
```

**Respuesta:**
```json
[
  {
    "date": "2026-02-10",
    "total_volume": 850000.00,
    "total_markets": 45,
    "avg_volume_per_market": 18888.89
  }
]
```

---

#### `GET /analytics/top-categories-by-liquidity`
Categorías con mayor liquidez

**Query Parameters:**
- `limit` (int, default=10): Número de categorías

---

#### `GET /analytics/market-metrics-summary`
Resumen general de métricas

**Respuesta:**
```json
{
  "total_markets": 1250,
  "active_markets": 890,
  "closed_markets": 360,
  "total_volume": 25000000.00,
  "avg_volume": 20000.00,
  "total_liquidity": 8500000.00,
  "avg_liquidity": 6800.00,
  "total_categories": 12
}
```

---

#### `GET /analytics/trending-markets`
Mercados con mayor actividad reciente

**Query Parameters:**
- `limit` (int, default=10): Número de mercados

**Respuesta:**
```json
[
  {
    "market_id": "0x123...",
    "question": "Who will win the Super Bowl?",
    "category": "Sports",
    "volume_24hr": 450000.00,
    "total_volume": 2500000.00,
    "outcome_price_yes": 0.62,
    "active": true
  }
]
```

---

## 💡 Ejemplos de Uso

### Python (requests)

```python
import requests

# Obtener top 5 mercados por volumen
response = requests.get('http://localhost:8000/markets/top-volume?limit=5')
data = response.json()

for market in data:
    print(f"{market['question']}: ${market['volume']:,.2f}")
```

### JavaScript (fetch)

```javascript
// Buscar mercados sobre crypto
fetch('http://localhost:8000/tags/search?name=crypto')
  .then(response => response.json())
  .then(tags => {
    tags.forEach(tag => {
      console.log(`${tag.label} (${tag.slug})`);
    });
  });
```

### cURL

```bash
# Obtener mercados que cierran en 24 horas
curl "http://localhost:8000/markets/closing-soon?hours=24"

# Buscar mercados de elecciones
curl "http://localhost:8000/markets/search/?query=election&limit=5"

# Obtener estadísticas por categoría
curl "http://localhost:8000/analytics/category-stats"
```

---

## 📚 Documentación Interactiva

FastAPI genera documentación automática e interactiva:

### Swagger UI
Accede a http://localhost:8000/docs

- ✅ Explorar todos los endpoints
- ✅ Probar requests directamente
- ✅ Ver esquemas de datos
- ✅ Validación en tiempo real

### ReDoc
Accede a http://localhost:8000/redoc

- ✅ Documentación legible
- ✅ Búsqueda de endpoints
- ✅ Ejemplos de código
- ✅ Descarga de especificación OpenAPI

---

## 🏗️ Arquitectura

```
fase3_api/
├── main.py                 # Aplicación principal FastAPI
├── config.py              # Configuración y settings
├── database.py            # Conexión a PostgreSQL
├── models.py              # Modelos Pydantic
├── routers/               # Routers modulares
│   ├── __init__.py
│   ├── markets.py        # Endpoints de markets
│   ├── events.py         # Endpoints de events
│   ├── series.py         # Endpoints de series
│   ├── tags.py           # Endpoints de tags
│   └── analytics.py      # Endpoints de analytics
├── requirements.txt       # Dependencias
├── .env                  # Variables de entorno
├── .env.example          # Plantilla de variables
├── run_api.bat           # Script de ejecución
└── README.md             # Documentación
```

### Flujo de Datos

```
Cliente HTTP
    ↓
FastAPI Router
    ↓
Pydantic Validation
    ↓
Database Query (PostgreSQL/NeonDB)
    ↓
Pydantic Response Model
    ↓
JSON Response
```

---

## 🔒 Seguridad

- ✅ Variables de entorno para credenciales
- ✅ Validación de entrada con Pydantic
- ✅ Queries parametrizadas (protección SQL injection)
- ✅ CORS configurado (ajustar en producción)
- ⚠️ En producción: agregar autenticación/autorización

---

## 🚀 Despliegue

Para desplegar en producción:

1. **Configurar CORS** específico en `config.py`
2. **Usar HTTPS** (certificado SSL/TLS)
3. **Variables de entorno** seguras
4. **Reverse proxy** (Nginx/Caddy)
5. **Rate limiting** para prevenir abuso
6. **Logs y monitoreo** (Sentry, LogRocket)

### Ejemplo con Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📝 Licencia y Autor

**Proyecto RA-2**  
**Fase 3: Exposición de Datos**  
Autor: Gabriel  
Fecha: Febrero 2026  

---

## 🤝 Contribución

Este proyecto es parte del curso de Data Engineering. Para contribuir al repositorio compartido de la clase:

GitHub Compartido: https://github.com/lasalle-ai/apis

---

## 📞 Soporte

Para problemas o preguntas:

1. Revisar la documentación interactiva en `/docs`
2. Verificar logs de la aplicación
3. Probar el endpoint `/health` para diagnóstico

---

**🎉 ¡API Lista para Usar!**

Visita http://localhost:8000/docs para comenzar a explorar los endpoints.
