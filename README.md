# FASE 1: Extracción de Datos de Polymarket API

## 📋 Descripción del Proyecto

Este proyecto implementa la **Fase 1** del ecosistema de datos sobre Polymarket, que consiste en la extracción automatizada de datos desde los endpoints públicos de la API de Polymarket.

## 🎯 Objetivos de la Fase 1

La Fase 1 se enfoca en la **recolección y almacenamiento de datos brutos** desde la API de Polymarket, extrayendo información de los siguientes endpoints:

- **Tags** 🏷️: Etiquetas utilizadas para categorizar eventos y mercados
- **Events** 📅: Eventos de predicción disponibles en la plataforma
- **Series** 📊: Series de eventos relacionados
- **Markets** 💹: Mercados de predicción individuales

## 🏗️ Arquitectura del Sistema

```
fase1_extraccion/
│
├── config.py                 # Configuración central del sistema
├── delta_utils.py            # Utilidades para Delta Lake
├── extract_tags.py           # Extractor de Tags
├── extract_events.py         # Extractor de Events
├── extract_series.py         # Extractor de Series
├── extract_markets.py        # Extractor de Markets
├── main.py                   # Script orquestador principal
├── check_delta.py            # Script de verificación Delta Lake
├── requirements.txt          # Dependencias del proyecto
│
├── delta_lake/               # ⭐ Directorio para tablas Delta Lake
│   ├── tags/
│   │   ├── part-*.snappy.parquet
│   │   └── _delta_log/
│   ├── events/
│   │   ├── part-*.snappy.parquet
│   │   └── _delta_log/
│   ├── series/
│   │   ├── part-*.snappy.parquet
│   │   └── _delta_log/
│   └── markets/
│       ├── part-*.snappy.parquet
│       └── _delta_log/
│
└── logs/                     # Directorio para logs de ejecución
    ├── delta_lake_YYYYMMDD.log
    ├── tags_extractor_YYYYMMDD.log
    ├── events_extractor_YYYYMMDD.log
    ├── series_extractor_YYYYMMDD.log
    ├── markets_extractor_YYYYMMDD.log
    └── main_extraction_YYYYMMDD_HHMMSS.log
```

## 📡 Endpoints de la API Polymarket

| Endpoint | URL | Descripción |
|----------|-----|-------------|
| **Tags** | `https://gamma-api.polymarket.com/tags` | Obtiene todas las etiquetas disponibles |
| **Events** | `https://gamma-api.polymarket.com/events` | Obtiene todos los eventos de predicción |
| **Series** | `https://gamma-api.polymarket.com/series` | Obtiene todas las series de eventos |
| **Markets** | `https://gamma-api.polymarket.com/markets` | Obtiene todos los mercados de predicción |

## � Formato de Almacenamiento: Delta Lake

El sistema utiliza **Delta Lake** como formato de almacenamiento principal, proporcionando:

### Características de Delta Lake

- **📦 Formato Parquet + Snappy**: Compresión eficiente (reducción de ~95% vs JSON)
- **🔒 Transacciones ACID**: Garantía de consistencia de datos
- **📜 Versionamiento**: Historial completo de cambios con "time travel"
- **🔄 Schema Evolution**: Capacidad de modificar esquemas sin reescribir datos
- **⚡ Performance**: Lectura columnar y predicado pushdown

### Comparación de Tamaños

| Tabla    | Formato Delta | Formato JSON | Reducción |
|----------|---------------|--------------|-----------|
| Tags     | 0.03 MB       | 0.13 MB      | 77%       |
| Events   | 0.88 MB       | 4.09 MB      | 78%       |
| Markets  | 0.75 MB       | 3.64 MB      | 79%       |
| Series   | 17.65 MB      | 424.29 MB    | **96%**   |
| **TOTAL**| **19.31 MB**  | **432.15 MB**| **95.5%** |

### Estructura de Tabla Delta

Cada tabla Delta contiene:
- `part-*.snappy.parquet`: Archivos de datos en formato Parquet
- `_delta_log/`: Log de transacciones con metadatos y versiones

## �🔧 Características Técnicas

### Funcionalidades Implementadas

✅ **Extracción por paginación**: Manejo automático de límites y offsets
✅ **Logging completo**: Registro detallado de todas las operaciones
✅ **Manejo de errores**: Captura y registro de excepciones
✅ **Configuración centralizada**: Parámetros ajustables desde `config.py`
✅ **Almacenamiento Delta Lake**: Formato empresarial con ACID, versionamiento y compresión
✅ **Ejecución modular**: Cada endpoint puede ejecutarse independientemente
✅ **Script orquestador**: Automatización de todas las extracciones
✅ **Metadatos de extracción**: Timestamp y fecha agregados automáticamente

### Parámetros Configurables

En el archivo `config.py` puedes ajustar:

- **limit**: Número de registros por petición (default: 500 - aumentado para eficiencia)
- **offset**: Offset inicial para paginación (default: 0)
- **max_records**: Máximo de registros a extraer (default: 0 = **SIN LÍMITE**, extrae todos los datos)
- **REQUEST_TIMEOUT**: Timeout de las peticiones HTTP (default: 30s)

> **IMPORTANTE**: Para extraer TODOS los datos disponibles, asegúrate de que `max_records = 0` en `config.py`

## 🚀 Instalación y Uso

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Dependencias Principales

- `requests==2.31.0` - Cliente HTTP para API calls
- `deltalake==0.19.0` - Formato Delta Lake
- `pandas==2.2.0` - Manipulación de datos
- `pyarrow==16.1.0` - Backend columnar para Parquet

### Instalación

1. Navega al directorio del proyecto:
```bash
cd "e:\Clases\Materias\Erick Venezolano (5074)\PROYECTO RA-2\fase1_extraccion"
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

### Ejecución

#### Opción 1: ⭐ EXTRACCIÓN COMPLETA SIN LÍMITES (Recomendado)

Para extraer **TODOS** los datos disponibles de la API sin límites:

**Usando el script dedicado:**
```bash
python extraer_completo.py
```

**O usando el archivo batch (Windows):**
```bash
extraer_completo.bat
```

**O usando el notebook interactivo:**
- Abre `extraer_datos_delta_lake.ipynb`
- Ve a la sección "2.5. RE-EXTRAER TODOS LOS DATOS DE LA API (SIN LÍMITES)"
- Ejecuta las celdas de extracción

Este comando:
- ✅ Extrae **TODOS** los registros disponibles (sin límite de 500)
- ✅ Utiliza paginación automática (500 registros por petición)
- ✅ Guarda los datos en Delta Lake con compresión
- ✅ Muestra progreso en tiempo real
- ✅ Genera logs detallados de la extracción

**Configuración actual** (en `config.py`):
- `limit`: 500 (registros por petición)
- `max_records`: 0 (sin límite = extrae todo)

#### Opción 2: Ejecutar extracción con límite (Modo legacy)

```bash
python main.py
```

Este comando ejecutará la extracción usando la configuración de `max_records` en `config.py`.

#### Opción 3: Ejecutar extractores individuales

Puedes ejecutar cada extractor de forma independiente:

```bash
# Extraer solo Tags
python extract_tags.py

# Extraer solo Events
python extract_events.py

# Extraer solo Series
python extract_series.py

# Extraer solo Markets
python extract_markets.py
```

#### Opción 4: Verificar Tablas Delta Lake

Para ver información detallada sobre las tablas Delta Lake generadas:

```bash
python check_delta.py
```

Este script muestra:
- Versión actual de cada tabla
- Número de archivos y tamaño total
- Número de registros y columnas
- Comparación con archivos JSON legacy

### Trabajar con Tablas Delta Lake

```python
from delta_utils import DeltaLakeManager

# Inicializar gestor
manager = DeltaLakeManager()

# Leer tabla completa
df = manager.read_delta_table("tags")

# Leer versión específica (time travel)
df_v0 = manager.read_delta_table("tags", version=0)

# Obtener información de tabla
info = manager.get_table_info("tags")
print(f"Versión: {info['version']}")

# Listar todas las tablas
tables = manager.list_tables()
print(tables)  # ['events', 'markets', 'series', 'tags']
```

## ⚡ Probar API con Thunder Client

Thunder Client es una extensión de VS Code que permite probar la API de Polymarket de forma visual sin escribir código.

### Instalación Rápida

1. En VS Code: `Ctrl+Shift+X`
2. Buscar: "Thunder Client"
3. Click en "Install"
4. Click en el ícono del rayo ⚡ en la barra lateral

### Importar Colección Pre-configurada

Hemos incluido una colección con **15 requests pre-configuradas** listas para usar:

```
1. Abre Thunder Client (⚡)
2. Ve a "Collections"
3. Click en el menú ⋮ → "Import"
4. Selecciona: thunder-collection_polymarket.json
5. ¡Listo! Ya puedes probar la API
```

### Requests Disponibles

La colección incluye:

- **Tags** (3 requests): Listar, paginación, obtener cantidades variables
- **Events** (5 requests): Todos, activos, featured, alta liquidez, por tag
- **Series** (3 requests): Todas, activas, featured
- **Markets** (4 requests): Todos, activos, alta liquidez, top volume

### Ejemplo Rápido

```
1. Expande la carpeta "Tags"
2. Click en "Tags - Listar Todos (10 primeros)"
3. Click en "Send" (botón azul)
4. ¡Ver respuesta JSON!
```

### Documentación Completa

- **[THUNDER_CLIENT_QUICKSTART.md](THUNDER_CLIENT_QUICKSTART.md)** - Guía visual paso a paso
- **[THUNDER_CLIENT_GUIA.md](THUNDER_CLIENT_GUIA.md)** - Guía completa con todos los parámetros

### Beneficios

✅ **Sin código**: Prueba la API visualmente
✅ **Rápido**: Click y enviar, ver resultados inmediatos
✅ **Aprendizaje**: Entiende cómo funcionan los endpoints
✅ **Debugging**: Compara datos API vs Delta Lake
✅ **Exploración**: Descubre nuevos parámetros y filtros

## 📊 Estructura de Datos Extraídos

### Tags
```json
[
  {
    "id": "string",
    "label": "string",
    "slug": "string",
    "forceShow": boolean,
    "publishedAt": "string",
    "createdBy": integer,
    "updatedBy": integer,
    "createdAt": "datetime",
    "updatedAt": "datetime",
    "forceHide": boolean,
    "isCarousel": boolean
  }
]
```

### Events
Los eventos contienen información detallada incluyendo:
- Información básica (id, título, descripción, slug)
- Fechas (startDate, endDate, creationDate)
- Métricas (liquidity, volume, openInterest)
- Relaciones (markets, series, tags, categories)
- Estado (active, closed, archived, featured)

### Series
Las series agrupan eventos relacionados con información sobre:
- Tipo de serie (seriesType, recurrence)
- Métricas agregadas (volume, liquidity)
- Eventos asociados
- Categorías y tags

### Markets
Los mercados contienen información completa sobre:
- Pregunta y descripción
- Resultados posibles (outcomes, outcomePrices)
- Métricas de trading (volume, liquidity, spread)
- Configuración del mercado (fees, limits)
- Estado de resolución

## 📈 Salida del Sistema

### Tablas Delta Lake Generadas

Cada ejecución crea/actualiza tablas Delta Lake en el directorio `delta_lake/`:

```
delta_lake/
├── tags/
│   ├── part-00001-*.snappy.parquet    # Datos en Parquet comprimido
│   └── _delta_log/
│       └── 00000000000000000000.json  # Log de transacciones
├── events/
│   ├── part-00001-*.snappy.parquet
│   └── _delta_log/
├── series/
│   ├── part-00001-*.snappy.parquet
│   └── _delta_log/
└── markets/
    ├── part-00001-*.snappy.parquet
    └── _delta_log/
```

**Beneficios del formato Delta:**
- Compresión superior (~95% reducción vs JSON)
- Versionamiento automático
- Transacciones ACID
- Lectura columnar eficiente

### Logs de Ejecución

Los logs se almacenan en el directorio `logs/` con información detallada:

```
logs/
├── tags_extractor_20260210.log
├── events_extractor_20260210.log
├── series_extractor_20260210.log
├── markets_extractor_20260210.log
└── main_extraction_20260210_143052.log
```

## 🎨 Ejemplo de Salida en Consola

```
============================================================
 POLYMARKET DATA EXTRACTOR - FASE 1 
============================================================

╔══════════════════════════════════════════════════════════╗
║         FASE 1: EXTRACCIÓN DE DATOS DE POLYMARKET        ║
╚══════════════════════════════════════════════════════════╝

============================================================
Iniciando extracción de TAGS
============================================================
INFO - Tags extraídos exitosamente: 150 registros
✓ Tags extraídos: 150 registros

============================================================
Iniciando extracción de EVENTS
============================================================
INFO - Events extraídos exitosamente: 500 registros
✓ Events extraídos: 500 registros

============================================================
Iniciando extracción de SERIES
============================================================
INFO - Series extraídas exitosamente: 75 registros
✓ Series extraídas: 75 registros

============================================================
Iniciando extracción de MARKETS
============================================================
INFO - Markets extraídos exitosamente: 500 registros
✓ Markets extraídos: 500 registros

============================================================
RESUMEN DE EXTRACCIÓN
============================================================
TAGS            - ✓ Exitoso   - 150 registros
EVENTS          - ✓ Exitoso   - 500 registros
SERIES          - ✓ Exitoso   - 75 registros
MARKETS         - ✓ Exitoso   - 500 registros
============================================================
Tiempo total de ejecución: 0:02:15.123456
============================================================

╔══════════════════════════════════════════════════════════╗
║              RESUMEN FINAL DE EXTRACCIÓN                 ║
╠══════════════════════════════════════════════════════════╣
║  TAGS         :    150 registros extraídos              ║
║  EVENTS       :    500 registros extraídos              ║
║  SERIES       :     75 registros extraídos              ║
║  MARKETS      :    500 registros extraídos              ║
╚══════════════════════════════════════════════════════════╝

✓ Todas las extracciones se completaron exitosamente
```

## 🔍 Verificación de Datos

Para verificar que los datos se extrajeron correctamente:

```python
from delta_utils import DeltaLakeManager

# Inicializar gestor de Delta Lake
manager = DeltaLakeManager()

# Leer tabla de tags
tags_df = manager.read_delta_table("tags")
print(f"Total de tags: {len(tags_df)}")
print(f"Columnas: {tags_df.columns.tolist()}")
print(f"\nPrimeros 5 registros:")
print(tags_df.head())

# Obtener información de la tabla
info = manager.get_table_info("tags")
print(f"\nVersión de la tabla: {info['version']}")
```
```

## ⚠️ Manejo de Errores

El sistema incluye manejo robusto de errores:

- **Timeout de conexión**: Configurable en `config.py`
- **Errores HTTP**: Se registran con código de estado
- **Errores de parsing**: Se capturan y registran
- **Interrupciones**: El usuario puede detener con Ctrl+C

## 📝 Próximos Pasos (Fases Futuras)

- **Fase 2**: Transformación y limpieza de datos
- **Fase 3**: Carga en Data Lake
- **Fase 4**: Modelado dimensional para Data Warehouse
- **Fase 5**: Análisis y visualización

## 👥 Autor

Proyecto RA-2: Ecosistema de Datos (Datalake & Datawarehouse)
Materia: Erick Venezolano (5074)

## 📄 Licencia

Este proyecto es con fines educativos.

## 🔗 Referencias

- [Documentación API Polymarket](https://docs.polymarket.com/)
- [Polymarket GitHub](https://github.com/polymarket)

---

**Fecha de Creación**: Febrero 10, 2026  
**Versión**: 1.0.0  
**Estado**: Fase 1 Completa ✅
