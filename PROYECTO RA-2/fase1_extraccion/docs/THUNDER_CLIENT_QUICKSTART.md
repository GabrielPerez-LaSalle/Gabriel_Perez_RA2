# ⚡ Thunder Client - Guía Rápida Visual

## 📥 Paso 1: Instalar Thunder Client

```
1. Presiona Ctrl+Shift+X (abrir extensiones)
2. Busca: "Thunder Client"
3. Click "Install"
4. Espera a que se instale
```

**Resultado**: Verás el ícono del rayo ⚡ en la barra lateral izquierda.

---

## 🎯 Paso 2: Abrir Thunder Client

```
Click en el ícono del rayo ⚡ en la barra lateral izquierda
```

**Vista de Thunder Client:**
```
┌─────────────────────────────────────┐
│ Thunder Client                   ⚡ │
├─────────────────────────────────────┤
│ Collections                         │
│ Env                                 │
│ Activity                            │
│                                     │
│ [New Request]                       │
└─────────────────────────────────────┘
```

---

## 🚀 Paso 3: Hacer tu Primera Request

### Opción A: Request Manual

**1. Click en "New Request"**

**2. Configurar la Request:**
```
┌─────────────────────────────────────────────────────────┐
│ GET ▼  https://gamma-api.polymarket.com/tags    [Send] │
├─────────────────────────────────────────────────────────┤
│ Query │ Headers │ Body │ Auth │ Tests │              │
├─────────────────────────────────────────────────────────┤
│ + Add Param                                             │
│                                                         │
│ Key            Value                                    │
│ limit          10                                       │
│ offset         0                                        │
└─────────────────────────────────────────────────────────┘
```

**3. Agregar Query Parameters:**
- Click en pestaña **"Query"**
- Click **"Add Param"**
- Agregar:
  - `limit`: `10`
  - `offset`: `0`

**4. Click botón azul "Send"**

**5. Ver Respuesta:**
```
┌─────────────────────────────────────────────────────────┐
│ Response ▼                                              │
├─────────────────────────────────────────────────────────┤
│ Status: 200 OK     Time: 245ms     Size: 2.3 KB        │
├─────────────────────────────────────────────────────────┤
│ Body │ Headers │ Cookies │                             │
├─────────────────────────────────────────────────────────┤
│ [                                                       │
│   {                                                     │
│     "id": "1",                                          │
│     "label": "Crypto",                                  │
│     "slug": "crypto",                                   │
│     "forceShow": false,                                 │
│     ...                                                 │
│   }                                                     │
│ ]                                                       │
└─────────────────────────────────────────────────────────┘
```

---

### Opción B: Importar Colección (MÁS FÁCIL) ⭐

**1. Click en "Collections" en Thunder Client**

**2. Click en el menú ⋮ (tres puntos)**

**3. Select "Import"**

**4. Seleccionar el archivo:**
```
thunder-collection_polymarket.json
```

**5. ¡Listo!** Verás la colección "Polymarket API" con 15 requests pre-configuradas.

---

## 📋 Requests Pre-configuradas Disponibles

Después de importar la colección, verás:

```
📁 Polymarket API
  │
  ├── 📁 Tags (3 requests)
  │   ├── Tags - Listar Todos (10 primeros)
  │   ├── Tags - Obtener 100
  │   └── Tags - Paginación (segunda página)
  │
  ├── 📁 Events (5 requests)
  │   ├── Events - Listar Todos (20 primeros)
  │   ├── Events - Solo Activos
  │   ├── Events - Solo Featured
  │   ├── Events - Alta Liquidez
  │   └── Events - Por Tag Crypto
  │
  ├── 📁 Series (3 requests)
  │   ├── Series - Listar Todas (20 primeras)
  │   ├── Series - Solo Activas
  │   └── Series - Featured
  │
  └── 📁 Markets (4 requests)
      ├── Markets - Listar Todos (30 primeros)
      ├── Markets - Solo Activos
      ├── Markets - Alta Liquidez
      └── Markets - Top Volume
```

---

## 🎮 Probar las Requests

### Para Tags:

1. Expande la carpeta **Tags**
2. Click en **"Tags - Listar Todos (10 primeros)"**
3. La request se cargará automáticamente
4. Click **"Send"**
5. Ver respuesta JSON

### Para Events:

1. Expande la carpeta **Events**
2. Click en **"Events - Solo Activos"**
3. Click **"Send"**
4. Verás todos los eventos activos

### Para Markets con Alta Liquidez:

1. Expande la carpeta **Markets**
2. Click en **"Markets - Alta Liquidez"**
3. Click **"Send"**
4. Verás markets con liquidez > 5000

---

## 🔧 Modificar Parámetros

Si quieres cambiar los parámetros de una request:

```
1. Click en la request que quieres modificar
2. Ve a la pestaña "Query"
3. Cambia los valores:
   - limit: cambia de 10 a 50
   - offset: cambia de 0 a 100
4. Click "Send" de nuevo
```

---

## 💾 Guardar una Request Nueva

Si creas una request nueva y quieres guardarla:

```
1. Después de configurar tu request
2. Click en "Save" (arriba a la derecha)
3. Dale un nombre: "Mi Custom Request"
4. Selecciona la carpeta: "Polymarket API"
5. Click "Save"
```

---

## 📊 Entender la Respuesta

### Status Codes

```
✅ 200 OK          - Todo correcto, datos recibidos
❌ 400 Bad Request - Parámetros incorrectos
❌ 404 Not Found   - Endpoint no existe
❌ 500 Server Error - Error del servidor
```

### Partes de la Respuesta

1. **Status**: Código HTTP (200 = éxito)
2. **Time**: Tiempo que tomó la request
3. **Size**: Tamaño de la respuesta
4. **Body**: Datos JSON recibidos
5. **Headers**: Metadatos de la respuesta

---

## 🎯 Ejemplos Prácticos

### Ejemplo 1: Comparar con Python

**En Thunder Client:**
```
GET https://gamma-api.polymarket.com/tags?limit=5&offset=0
```

**En Python (nuestro código):**
```python
from extract_tags import TagsExtractor
extractor = TagsExtractor()
tags = extractor.extract_tags(limit=5, offset=0)
```

**Resultado**: Deberían ser los mismos datos.

---

### Ejemplo 2: Verificar Delta Lake

**Paso 1 - Thunder Client:**
```
GET https://gamma-api.polymarket.com/events?limit=10&active=true
```
→ Copia el primer ID que veas

**Paso 2 - Python:**
```python
from delta_utils import DeltaLakeManager
manager = DeltaLakeManager()
df = manager.read_delta_table("events")
# Buscar ese ID en el DataFrame
print(df[df['id'] == 'ID_COPIADO'])
```

**Resultado**: Deberías encontrar el mismo evento.

---

## 🆘 Solución de Problemas

### Problema: No veo el botón "Send"

**Solución:**
- Asegúrate de haber ingresado una URL válida
- El método debe estar seleccionado (GET)

### Problema: Response vacía []

**Solución:**
- Normal, significa que no hay datos con esos filtros
- Prueba con menos filtros o aumenta el `limit`

### Problema: Error 400

**Solución:**
- Revisa los query parameters
- Los booleanos deben ser: `true` o `false` (minúsculas)
- Los números NO deben tener comillas

### Problema: Request muy lenta

**Solución:**
- Reduce el `limit` (menos datos = más rápido)
- Verifica tu conexión a internet

---

## ⚡ Atajos de Teclado

```
Ctrl+Enter    - Enviar request
Ctrl+L        - Limpiar respuesta
Ctrl+S        - Guardar request
```

---

## 🎓 Ejercicio Final

**Objetivo**: Obtener los 5 tags más populares y buscar eventos relacionados.

### Paso 1: Obtener Tags
```
Request: Tags - Obtener 100
Method: GET
Click: Send
Acción: Anota 2-3 slugs interesantes (ej: "crypto", "sports")
```

### Paso 2: Buscar Events por Tag
```
Request: Crear nueva
Method: GET
URL: https://gamma-api.polymarket.com/events
Query Params:
  - limit: 20
  - offset: 0
  - tag_slug: crypto    ← usa el slug que anotaste
Click: Send
```

### Paso 3: Analizar
```
Pregunta: ¿Cuántos eventos encontraste?
Pregunta: ¿Cuál tiene mayor liquidez?
Pregunta: ¿Hay eventos featured?
```

---

## 📚 Próximos Pasos

1. ✅ Importar colección de Thunder Client
2. ✅ Probar cada carpeta (Tags, Events, Series, Markets)
3. ✅ Modificar parámetros y ver diferentes resultados
4. ✅ Comparar con datos extraídos en Delta Lake
5. ✅ Crear tus propias custom requests

---

## 🎯 Resumen de URLs

```
Tags:    https://gamma-api.polymarket.com/tags
Events:  https://gamma-api.polymarket.com/events
Series:  https://gamma-api.polymarket.com/series
Markets: https://gamma-api.polymarket.com/markets
```

**Todos usan GET y requieren `limit` y `offset` mínimo.**

---

**¡Listo! Ya puedes explorar la API de Polymarket como un pro! 🚀**
