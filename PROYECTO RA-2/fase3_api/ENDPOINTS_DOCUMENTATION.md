# ============================================================
# DOCUMENTACIÓN DE ENDPOINTS PARA GITHUB COMPARTIDO
# Repositorio: https://github.com/lasalle-ai/apis
# Proyecto: Polymarket Data Warehouse API
# Autor: Gabriel
# ============================================================

## API Info

- **Nombre**: Polymarket Data Warehouse API
- **Versión**: 1.0.0
- **Tecnología**: FastAPI + PostgreSQL (NeonDB)
- **Base URL**: `http://localhost:8000` (desarrollo)
- **Documentación**: `http://localhost:8000/docs`

---

## 📋 Endpoints Disponibles

### 1. Markets - Top Volume

**Endpoint**: `GET /markets/top-volume`

**Descripción**: Devuelve los N mercados con más volumen total de su categoría.

**Query Parameters**:
- `limit` (int, default=10): Número de resultados (1-100)
- `category` (string, optional): Filtrar por categoría específica

**Ejemplo Request**:
```
GET /markets/top-volume?limit=10&category=Sports
```

**Ejemplo Response**:
```json
[
  {
    "market_id": "0x1234567890abcdef",
    "question": "Will the Lakers win the NBA Championship 2026?",
    "category": "Sports",
    "volume": 2500000.50,
    "volume_24hr": 150000.00,
    "liquidity": 800000.00,
    "outcome_price_yes": 0.65
  }
]
```

**Caso de Uso**: Identificar los mercados más activos por volumen para analizar dónde se concentra el interés de trading.

---

### 2. Series - Probability Evolution

**Endpoint**: `GET /series/{series_id}/probability`

**Descripción**: Devuelve la evolución de probabilidad media de una serie específica a lo largo del tiempo.

**Path Parameters**:
- `series_id` (string): ID de la serie

**Query Parameters**:
- `days` (int, default=30): Número de días de historial (1-365)

**Ejemplo Request**:
```
GET /series/nba-playoffs-2026/probability?days=30
```

**Ejemplo Response**:
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

**Caso de Uso**: Analizar tendencias de probabilidades en series recurrentes (ej: NBA, Elections) para identificar patrones.

---

### 3. Tags - Search

**Endpoint**: `GET /tags/search`

**Descripción**: Devuelve todos los tags relacionados con un término de búsqueda específico.

**Query Parameters**:
- `name` (string, required, min=3): Término de búsqueda (ej: 'crypto', 'politics')
- `limit` (int, default=20): Número de resultados (1-100)

**Ejemplo Request**:
```
GET /tags/search?name=crypto&limit=10
```

**Ejemplo Response**:
```json
[
  {
    "tag_id": "crypto-bitcoin",
    "label": "Bitcoin",
    "slug": "bitcoin",
    "level": 2
  },
  {
    "tag_id": "crypto-ethereum",
    "label": "Ethereum",
    "slug": "ethereum",
    "level": 2
  }
]
```

**Caso de Uso**: Descubrir categorías y subcategorías relacionadas con temas específicos para filtrado avanzado.

---

### 4. Events - Closing Soon

**Endpoint**: `GET /events/closing-soon/list`

**Descripción**: Lista de eventos que finalizan en las próximas 24-48 horas (configurable).

**Query Parameters**:
- `hours` (int, default=48): Horas hasta el cierre (1-168)
- `limit` (int, default=20): Número de resultados (1-100)

**Ejemplo Request**:
```
GET /events/closing-soon/list?hours=24&limit=15
```

**Ejemplo Response**:
```json
[
  {
    "event_id": 12345,
    "title": "Super Bowl LVIII Winner",
    "slug": "super-bowl-lviii-2026",
    "category": "Sports",
    "subcategory": "NFL",
    "active": true,
    "closed": false
  }
]
```

**Caso de Uso**: Alertas y notificaciones de eventos próximos a finalizar para oportunidades de último momento.

---

### 5. Markets - Closing Soon (Detallado)

**Endpoint**: `GET /markets/closing-soon`

**Descripción**: Mercados activos que finalizarán en las próximas N horas con métricas detalladas.

**Query Parameters**:
- `hours` (int, default=48): Horas hasta el cierre (1-168)
- `limit` (int, default=20): Número de resultados (1-100)

**Ejemplo Request**:
```
GET /markets/closing-soon?hours=24&limit=10
```

**Ejemplo Response**:
```json
[
  {
    "market_id": "0xabcd1234",
    "question": "Will it rain in NYC tomorrow?",
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

**Caso de Uso**: Dashboard de trading para identificar oportunidades de cierre inminente con métricas de decisión.

---

### 6. Analytics - Category Stats

**Endpoint**: `GET /analytics/category-stats`

**Descripción**: Obtiene estadísticas agregadas por categoría (mercados, volumen, liquidez).

**Query Parameters**:
- `limit` (int, default=20): Número de categorías (1-100)

**Ejemplo Request**:
```
GET /analytics/category-stats?limit=5
```

**Ejemplo Response**:
```json
[
  {
    "category": "Sports",
    "total_markets": 245,
    "active_markets": 180,
    "total_volume": 5500000.00,
    "avg_volume": 22448.98,
    "total_liquidity": 1200000.00
  },
  {
    "category": "Crypto",
    "total_markets": 189,
    "active_markets": 145,
    "total_volume": 4200000.00,
    "avg_volume": 22222.22,
    "total_liquidity": 950000.00
  }
]
```

**Caso de Uso**: Dashboard analítico para comparar actividad entre categorías y tomar decisiones de inversión.

---

### 7. Tags - Markets by Tag

**Endpoint**: `GET /tags/{tag_id}/markets`

**Descripción**: Obtiene todos los mercados relacionados con un tag específico.

**Path Parameters**:
- `tag_id` (string): ID del tag

**Query Parameters**:
- `active_only` (bool, default=true): Solo mercados activos
- `limit` (int, default=50): Número de mercados (1-200)

**Ejemplo Request**:
```
GET /tags/crypto-bitcoin/markets?active_only=true&limit=20
```

**Ejemplo Response**:
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
      "market_id": "0x9876543210",
      "question": "Will Bitcoin reach $100,000 in 2026?",
      "slug": "btc-100k-2026",
      "category": "Crypto",
      "subcategory": "Bitcoin",
      "active": true,
      "closed": false
    }
  ]
}
```

**Caso de Uso**: Filtrar todos los mercados de una categoría específica (ej: todos los mercados de Bitcoin).

---

### 8. Analytics - Volume Trends

**Endpoint**: `GET /analytics/volume-trends`

**Descripción**: Tendencias de volumen diario a lo largo del tiempo, opcionalmente filtrado por categoría.

**Query Parameters**:
- `days` (int, default=30): Número de días de historial (1-365)
- `category` (string, optional): Filtrar por categoría

**Ejemplo Request**:
```
GET /analytics/volume-trends?days=7&category=Sports
```

**Ejemplo Response**:
```json
[
  {
    "date": "2026-02-10",
    "total_volume": 850000.00,
    "total_markets": 45,
    "avg_volume_per_market": 18888.89
  },
  {
    "date": "2026-02-11",
    "total_volume": 920000.00,
    "total_markets": 48,
    "avg_volume_per_market": 19166.67
  }
]
```

**Caso de Uso**: Visualización de gráficos de tendencias para análisis temporal de actividad.

---

### 9. Markets - Search

**Endpoint**: `GET /markets/search/`

**Descripción**: Búsqueda de mercados por palabras clave en la pregunta.

**Query Parameters**:
- `query` (string, required, min=3): Término de búsqueda
- `limit` (int, default=20): Número de resultados (1-100)

**Ejemplo Request**:
```
GET /markets/search/?query=election&limit=10
```

**Ejemplo Response**:
```json
[
  {
    "market_id": "0xelection123",
    "question": "Who will win the 2026 Presidential Election?",
    "slug": "presidential-election-2026",
    "category": "Politics",
    "subcategory": "Elections",
    "active": true,
    "closed": false
  }
]
```

**Caso de Uso**: Buscador de mercados para usuarios finales o integración con sistemas de búsqueda.

---

### 10. Analytics - Trending Markets

**Endpoint**: `GET /analytics/trending-markets`

**Descripción**: Mercados con mayor volumen en las últimas 24 horas (trending).

**Query Parameters**:
- `limit` (int, default=10): Número de mercados (1-50)

**Ejemplo Request**:
```
GET /analytics/trending-markets?limit=5
```

**Ejemplo Response**:
```json
[
  {
    "market_id": "0xtrending123",
    "question": "Will Trump win Republican Primary?",
    "category": "Politics",
    "volume_24hr": 450000.00,
    "total_volume": 2500000.00,
    "outcome_price_yes": 0.62,
    "active": true
  }
]
```

**Caso de Uso**: Sección "Trending Now" en aplicaciones web/móviles para mostrar mercados populares.

---

## 🔧 Información Técnica

### Autenticación
- **Tipo**: Ninguna (API pública en desarrollo)
- **Producción**: Se recomienda implementar API Keys o OAuth2

### Rate Limiting
- **Actual**: No implementado
- **Recomendado**: 100 requests/minuto por IP

### Formatos de Respuesta
- **Content-Type**: `application/json`
- **Encoding**: UTF-8

### Códigos de Estado HTTP
- `200`: Éxito
- `404`: Recurso no encontrado
- `422`: Error de validación de parámetros
- `500`: Error interno del servidor

### Paginación
Endpoints con `limit` y `offset` para paginación:
- `limit`: Número de resultados por página
- `offset`: Número de resultados a saltar

**Ejemplo**:
```
GET /markets/category/Sports?limit=20&offset=0   # Página 1
GET /markets/category/Sports?limit=20&offset=20  # Página 2
```

---

## 📚 Documentación Completa

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## 🚀 Instalación y Ejecución

### Prerrequisitos
- Python 3.10+
- PostgreSQL (NeonDB)

### Pasos Rápidos
```bash
cd fase3_api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

La API estará disponible en `http://localhost:8000`

---

## 📞 Contacto

**Estudiante**: Gabriel  
**Proyecto**: RA-2 Data Engineering  
**Repositorio Individual**: [Tu GitHub]  
**Repositorio Compartido**: https://github.com/lasalle-ai/apis

---

## 📝 Notas

1. **Datos**: Los datos provienen de un Data Warehouse con información de Polymarket
2. **Actualización**: Los datos se actualizan según el pipeline ETL (Fases 1 y 2)
3. **Performance**: Queries optimizadas con índices en PostgreSQL
4. **Escalabilidad**: Diseñado para soportar miles de requests con caching futuro

---

**Fecha de Creación**: Febrero 2026  
**Última Actualización**: Febrero 17, 2026
