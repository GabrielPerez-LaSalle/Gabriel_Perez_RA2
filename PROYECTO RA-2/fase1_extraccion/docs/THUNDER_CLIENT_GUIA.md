# 🌩️ Guía Thunder Client - API Polymarket

## ¿Qué es Thunder Client?

Thunder Client es una extensión de VS Code que permite hacer peticiones HTTP directamente desde el editor, similar a Postman pero integrado en VS Code.

---

## 📥 Instalación de Thunder Client

1. En VS Code, presiona `Ctrl+Shift+X` para abrir Extensions
2. Busca "Thunder Client"
3. Haz clic en "Install"
4. Verás el ícono del rayo ⚡ en la barra lateral izquierda

---

## 📡 Endpoints de la API Polymarket

**Base URL**: `https://gamma-api.polymarket.com`

| Endpoint | URL Completa | Descripción |
|----------|--------------|-------------|
| Tags | `https://gamma-api.polymarket.com/tags` | Lista de etiquetas |
| Events | `https://gamma-api.polymarket.com/events` | Lista de eventos |
| Series | `https://gamma-api.polymarket.com/series` | Lista de series |
| Markets | `https://gamma-api.polymarket.com/markets` | Lista de mercados |

---

## 🚀 Cómo Usar Thunder Client

### 1. Abrir Thunder Client

- Haz clic en el ícono del rayo ⚡ en la barra lateral izquierda
- O presiona `Ctrl+Shift+P` y escribe "Thunder Client"

### 2. Crear una Nueva Request

1. Haz clic en **"New Request"**
2. Selecciona el método **GET**
3. Ingresa la URL del endpoint

---

## 📋 Ejemplos de Requests

### Ejemplo 1: Obtener 10 Tags

**Configuración:**
```
Método: GET
URL: https://gamma-api.polymarket.com/tags
```

**Query Parameters (pestaña Query):**
```
limit: 10
offset: 0
```

**Pasos en Thunder Client:**
1. Selecciona método **GET**
2. Pega la URL: `https://gamma-api.polymarket.com/tags`
3. Ve a la pestaña **Query**
4. Agrega parámetros:
   - Key: `limit`, Value: `10`
   - Key: `offset`, Value: `0`
5. Haz clic en **Send**

---

### Ejemplo 2: Obtener Events Activos

**Configuración:**
```
Método: GET
URL: https://gamma-api.polymarket.com/events
```

**Query Parameters:**
```
limit: 20
offset: 0
active: true
```

**Pasos:**
1. Método: **GET**
2. URL: `https://gamma-api.polymarket.com/events`
3. Query Parameters:
   - `limit` = `20`
   - `offset` = `0`
   - `active` = `true`
4. Click **Send**

---

### Ejemplo 3: Obtener Series por Slug

**Configuración:**
```
Método: GET
URL: https://gamma-api.polymarket.com/series
```

**Query Parameters:**
```
limit: 10
offset: 0
slug: crypto
```

---

### Ejemplo 4: Markets con Liquidez Mínima

**Configuración:**
```
Método: GET
URL: https://gamma-api.polymarket.com/markets
```

**Query Parameters:**
```
limit: 50
offset: 0
liquidity_min: 1000
active: true
```

---

## 🔧 Parámetros Comunes

### Parámetros de Paginación (TODOS los endpoints)

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `limit` | integer | Sí | Número de registros (≥0) |
| `offset` | integer | Sí | Desde qué registro empezar |

### Parámetros de Filtrado (Events)

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `active` | boolean | Solo eventos activos | `true` |
| `archived` | boolean | Solo eventos archivados | `false` |
| `featured` | boolean | Solo eventos destacados | `true` |
| `tag_id` | integer | Filtrar por ID de tag | `5` |
| `tag_slug` | string | Filtrar por slug de tag | `crypto` |
| `liquidity_min` | number | Liquidez mínima | `1000` |
| `liquidity_max` | number | Liquidez máxima | `100000` |
| `volume_min` | number | Volumen mínimo | `5000` |
| `start_date_min` | datetime | Fecha inicio desde | `2026-01-01T00:00:00Z` |
| `end_date_max` | datetime | Fecha fin hasta | `2026-12-31T23:59:59Z` |
| `closed` | boolean | Solo mercados cerrados | `false` |

### Parámetros de Ordenamiento

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `order` | string | Campos para ordenar | `liquidity,volume` |
| `ascending` | boolean | Orden ascendente | `false` |

---

## 💡 Tips y Trucos

### 1. Guardar Requests

- Después de crear una request, haz clic en **Save**
- Dale un nombre descriptivo: "Tags - 10 Primeros"
- Se guardará en la colección para reutilizar

### 2. Ver Respuesta Formateada

- La respuesta JSON se mostrará formateada automáticamente
- Usa las pestañas **Body**, **Headers**, **Cookies** para ver diferentes partes

### 3. Copiar como cURL

- Haz clic derecho en una request guardada
- Selecciona **"Copy as cURL"**
- Pégalo en terminal para ejecutar

### 4. Variables de Entorno

Puedes crear variables para reutilizar:

1. Click en el ícono de engranaje ⚙️
2. Ve a **Env**
3. Crea una variable:
   ```
   base_url: https://gamma-api.polymarket.com
   ```
4. Úsala en requests: `{{base_url}}/tags`

---

## 📊 Ejemplos de Consultas Complejas

### Consulta 1: Events Activos con Alta Liquidez

```
URL: https://gamma-api.polymarket.com/events

Query Parameters:
- limit: 50
- offset: 0
- active: true
- liquidity_min: 10000
- order: liquidity
- ascending: false
```

**Resultado**: Top 50 eventos activos ordenados por liquidez descendente.

---

### Consulta 2: Markets de Crypto Activos

```
URL: https://gamma-api.polymarket.com/markets

Query Parameters:
- limit: 100
- offset: 0
- active: true
- tag_slug: crypto
- closed: false
```

---

### Consulta 3: Tags Destacados

```
URL: https://gamma-api.polymarket.com/tags

Query Parameters:
- limit: 20
- offset: 0
- featured: true
```

---

### Consulta 4: Series con Eventos Futuros

```
URL: https://gamma-api.polymarket.com/series

Query Parameters:
- limit: 30
- offset: 0
- active: true
- start_date_min: 2026-02-01T00:00:00Z
```

---

## 🎨 Comparar con Python

### Thunder Client
```
GET https://gamma-api.polymarket.com/tags?limit=10&offset=0
```

### Equivalente en Python (nuestro código)
```python
from extract_tags import TagsExtractor

extractor = TagsExtractor()
tags = extractor.extract_tags(limit=10, offset=0)
```

---

## 🔍 Verificar Datos Extraídos

Para comparar datos entre Thunder Client y Delta Lake:

1. **Obtener datos en Thunder Client**:
   ```
   GET https://gamma-api.polymarket.com/tags?limit=5&offset=0
   ```

2. **Leer desde Delta Lake**:
   ```python
   from delta_utils import DeltaLakeManager
   manager = DeltaLakeManager()
   df = manager.read_delta_table("tags")
   print(df.head(5))
   ```

3. **Comparar**: Los IDs y datos deben coincidir

---

## 📝 Colección Thunder Client

Puedes importar la colección de requests pre-configuradas:

**Archivo**: `thunder-collection_polymarket.json` (ver carpeta del proyecto)

**Para importar:**
1. Abre Thunder Client
2. Ve a **Collections**
3. Click en el menú ⋮ → **Import**
4. Selecciona el archivo JSON
5. ¡Listo! Tendrás todas las requests configuradas

---

## ⚠️ Notas Importantes

1. **Sin Autenticación**: La API de Polymarket es pública, no requiere API key
2. **Rate Limits**: Ten cuidado con hacer muchas requests muy rápido
3. **Datos en Tiempo Real**: Los datos cambian constantemente (liquidez, volumen, etc.)
4. **Fechas**: Usar formato ISO 8601: `YYYY-MM-DDTHH:MM:SSZ`

---

## 🆘 Troubleshooting

### Error: "Failed to fetch"
- Verifica tu conexión a internet
- La URL debe ser exacta (sin espacios)

### Error: Status 400 (Bad Request)
- Revisa los parámetros de query
- Los valores booleanos deben ser `true` o `false` (minúsculas)
- Los números no deben tener comillas

### Error: Status 404 (Not Found)
- Verifica que la URL esté correcta
- El endpoint debe existir en la API

### Respuesta vacía []
- Normal si no hay datos que coincidan con los filtros
- Prueba con menos filtros o diferentes valores

---

## 🎯 Ejercicios Prácticos

### Ejercicio 1: Explorar Tags
1. Obtén los primeros 20 tags
2. Identifica el `slug` de un tag interesante
3. Usa ese slug para filtrar eventos

### Ejercicio 2: Comparar Liquidez
1. Obtén los 10 markets con mayor liquidez
2. Compara con los datos extraídos en Delta Lake
3. ¿Cuál tiene la liquidez más alta?

### Ejercicio 3: Time Travel
1. Extrae datos actuales con Thunder Client
2. Ejecuta `python main.py` para guardar en Delta Lake
3. Compara versión actual vs anterior usando Delta Lake versioning

---

## 📚 Recursos Adicionales

- **Documentación Oficial**: https://docs.polymarket.com/api-reference
- **Thunder Client Docs**: https://www.thunderclient.com/
- **ISO 8601 Dates**: https://www.iso.org/iso-8601-date-and-time-format.html

---

**Tip Final**: Guarda tus requests más usadas en una colección llamada "Polymarket API" para acceso rápido. 🚀
