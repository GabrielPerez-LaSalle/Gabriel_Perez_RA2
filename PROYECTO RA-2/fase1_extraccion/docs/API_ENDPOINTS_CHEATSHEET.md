# 🎯 API Endpoints - Cheat Sheet

## 📡 Base URL
```
https://gamma-api.polymarket.com
```

---

## 🏷️ TAGS

### Endpoint
```
GET /tags
```

### URL Completa
```
https://gamma-api.polymarket.com/tags
```

### Parámetros Obligatorios
| Parámetro | Tipo | Ejemplo |
|-----------|------|---------|
| `limit` | integer | `10` |
| `offset` | integer | `0` |

### Ejemplo Thunder Client
```
GET https://gamma-api.polymarket.com/tags?limit=10&offset=0
```

### Ejemplo cURL
```bash
curl "https://gamma-api.polymarket.com/tags?limit=10&offset=0"
```

---

## 📅 EVENTS

### Endpoint
```
GET /events
```

### URL Completa
```
https://gamma-api.polymarket.com/events
```

### Parámetros Obligatorios
| Parámetro | Tipo | Ejemplo |
|-----------|------|---------|
| `limit` | integer | `20` |
| `offset` | integer | `0` |

### Parámetros Opcionales Más Usados
| Parámetro | Tipo | Ejemplo | Descripción |
|-----------|------|---------|-------------|
| `active` | boolean | `true` | Solo eventos activos |
| `featured` | boolean | `true` | Solo destacados |
| `tag_slug` | string | `crypto` | Filtrar por tag |
| `liquidity_min` | number | `10000` | Liquidez mínima |
| `liquidity_max` | number | `100000` | Liquidez máxima |
| `volume_min` | number | `5000` | Volumen mínimo |
| `closed` | boolean | `false` | Excluir cerrados |

### Ejemplos Thunder Client

**Eventos Activos:**
```
GET https://gamma-api.polymarket.com/events?limit=20&offset=0&active=true
```

**Alta Liquidez:**
```
GET https://gamma-api.polymarket.com/events?limit=30&offset=0&liquidity_min=10000&active=true
```

**Por Tag Crypto:**
```
GET https://gamma-api.polymarket.com/events?limit=25&offset=0&tag_slug=crypto
```

---

## 📊 SERIES

### Endpoint
```
GET /series
```

### URL Completa
```
https://gamma-api.polymarket.com/series
```

### Parámetros Obligatorios
| Parámetro | Tipo | Ejemplo |
|-----------|------|---------|
| `limit` | integer | `20` |
| `offset` | integer | `0` |

### Parámetros Opcionales
| Parámetro | Tipo | Ejemplo | Descripción |
|-----------|------|---------|-------------|
| `active` | boolean | `true` | Solo series activas |
| `featured` | boolean | `true` | Solo destacadas |
| `closed` | boolean | `false` | Excluir cerradas |

### Ejemplos Thunder Client

**Series Activas:**
```
GET https://gamma-api.polymarket.com/series?limit=50&offset=0&active=true
```

**Series Featured:**
```
GET https://gamma-api.polymarket.com/series?limit=15&offset=0&featured=true
```

---

## 💹 MARKETS

### Endpoint
```
GET /markets
```

### URL Completa
```
https://gamma-api.polymarket.com/markets
```

### Parámetros Obligatorios
| Parámetro | Tipo | Ejemplo |
|-----------|------|---------|
| `limit` | integer | `30` |
| `offset` | integer | `0` |

### Parámetros Opcionales Más Usados
| Parámetro | Tipo | Ejemplo | Descripción |
|-----------|------|---------|-------------|
| `active` | boolean | `true` | Solo mercados activos |
| `closed` | boolean | `false` | Excluir cerrados |
| `liquidity_min` | number | `5000` | Liquidez mínima |
| `liquidity_max` | number | `50000` | Liquidez máxima |
| `volume_min` | number | `10000` | Volumen mínimo |
| `volume_max` | number | `200000` | Volumen máximo |

### Ejemplos Thunder Client

**Markets Activos:**
```
GET https://gamma-api.polymarket.com/markets?limit=50&offset=0&active=true&closed=false
```

**Alta Liquidez:**
```
GET https://gamma-api.polymarket.com/markets?limit=20&offset=0&liquidity_min=5000&active=true
```

**Top Volume:**
```
GET https://gamma-api.polymarket.com/markets?limit=25&offset=0&volume_min=10000
```

---

## 🔧 Parámetros Universales

### Paginación
```
limit:  Cantidad de registros a obtener (≥0)
offset: Desde qué registro empezar (≥0)
```

### Ordenamiento
```
order:     Campos para ordenar (comma-separated)
ascending: true/false - Orden ascendente/descendente
```

**Ejemplo:**
```
?limit=10&offset=0&order=liquidity,volume&ascending=false
```

---

## 📋 Formatos de Valores

### Booleanos
```
✅ Correcto: true, false (minúsculas)
❌ Incorrecto: True, False, TRUE, FALSE
```

### Números
```
✅ Correcto: 10000, 5000.5
❌ Incorrecto: "10000", "5000"
```

### Strings
```
✅ Correcto: crypto, sports, politics
❌ Incorrecto: "crypto", CRYPTO
```

### Fechas (ISO 8601)
```
✅ Correcto: 2026-02-01T00:00:00Z
❌ Incorrecto: 2026-02-01, 01/02/2026
```

---

## 🎯 Quick Reference

### Obtener Primeros 10 de Cada Endpoint

```bash
# Tags
curl "https://gamma-api.polymarket.com/tags?limit=10&offset=0"

# Events
curl "https://gamma-api.polymarket.com/events?limit=10&offset=0"

# Series
curl "https://gamma-api.polymarket.com/series?limit=10&offset=0"

# Markets
curl "https://gamma-api.polymarket.com/markets?limit=10&offset=0"
```

---

## 📊 Response Format

Todos los endpoints devuelven:

```json
[
  {
    "id": "...",
    "field1": "...",
    "field2": 123,
    ...
  },
  {
    "id": "...",
    ...
  }
]
```

**Tipo:** Array de objetos JSON
**Status Code Éxito:** 200 OK
**Content-Type:** application/json

---

## 🚀 Casos de Uso Comunes

### 1. Explorar Datos Nuevos
```
GET /tags?limit=100&offset=0
→ Ver todos los tags disponibles
```

### 2. Monitorear Eventos Activos
```
GET /events?limit=50&offset=0&active=true
→ Ver eventos en curso
```

### 3. Encontrar Oportunidades (Alta Liquidez)
```
GET /markets?limit=30&offset=0&liquidity_min=10000&active=true
→ Mercados con buena liquidez
```

### 4. Análisis por Categoría
```
GET /events?limit=100&offset=0&tag_slug=crypto
→ Todos los eventos de crypto
```

### 5. Paginación (Extraer Todo)
```
Página 1: offset=0, limit=100
Página 2: offset=100, limit=100
Página 3: offset=200, limit=100
...
```

---

## 🎓 Testing Workflow

```
1. Thunder Client → Probar endpoint manualmente
2. Verificar respuesta (200 OK, datos correctos)
3. Copiar parámetros exitosos
4. Usar en Python scripts (extract_*.py)
5. Guardar en Delta Lake
6. Comparar datos Thunder Client vs Delta Lake
```

---

## 📚 Documentación Completa

- **API Docs**: https://docs.polymarket.com/api-reference
- **Thunder Client Guide**: THUNDER_CLIENT_GUIA.md
- **Quick Start**: THUNDER_CLIENT_QUICKSTART.md
- **Collection**: thunder-collection_polymarket.json

---

**Nota**: Todos los endpoints son públicos, no requieren autenticación. 🔓
