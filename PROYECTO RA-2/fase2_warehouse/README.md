# ============================================================
# FASE 2: DATA WAREHOUSE EN NEONDB (CAPA GOLD)
# ============================================================

Este directorio contiene todos los scripts necesarios para implementar la Fase 2 del proyecto: 
el Data Warehouse en NeonDB con modelado dimensional optimizado para análisis.

## 📋 Contenido

- `schema_ddl.sql` - Script SQL con el DDL completo del esquema dimensional
- `neondb_config.py` - Configuración de conexión a NeonDB
- `create_schema.py` - Script para crear las tablas en NeonDB
- `etl_warehouse.py` - ETL completo: Delta Lake → NeonDB
- `README.md` - Esta documentación

## 🏗️ Arquitectura del Data Warehouse

### Modelo Dimensional (Star Schema)

El Data Warehouse implementa un **esquema en estrella** con las siguientes componentes:

#### Dimensiones:

1. **dim_time** - Dimensión de tiempo
   - Granularidad: Diaria
   - Atributos: año, trimestre, mes, semana, día, indicadores de período
   - Rango: 2021-01-01 a 2026-12-31

2. **dim_series** - Dimensión de series de mercados
   - Series como: NBA, Elections, Crypto, etc.
   - Tipo: SCD Type 2 (Slowly Changing Dimension)

3. **dim_event** - Dimensión de eventos
   - Eventos que contienen múltiples mercados
   - Incluye metadata deportiva cuando aplica

4. **dim_market** - Dimensión de mercados
   - Mercados de predicción individuales
   - Outcomes almacenados como JSONB

5. **dim_tag** - Dimensión de tags con jerarquía
   - Estructura jerárquica multinivel
   - Path para navegación de jerarquía

#### Tabla Puente:

- **bridge_market_tag** - Relación many-to-many entre markets y tags

#### Tabla de Hechos:

- **fact_market_metrics** - Métricas de mercado
  - Volumen (total, 24h, 1w, 1m, 1y)
  - Liquidez (AMM, CLOB)
  - Precios (desanidados: Yes/No, bid/ask, last trade)
  - Open Interest
  - Cambios de precio (1h, 1d, 1w, 1m, 1y)
  - Engagement (comentarios, tweets)
  - Fees

## 🚀 Instalación y Configuración

### 1. Instalar dependencias

```bash
pip install psycopg2-binary python-dotenv
```

### 2. Configurar conexión a NeonDB

Las credenciales están configuradas en `neondb_config.py`:

- **Project ID**: `rapid-shape-37645142`
- **Project Name**: `gabrieldev_RA2`
- **Branch Development**: `br-solitary-paper-aixy2j6f`
- **Branch Production**: `br-cold-tooth-aipr1qpz`

### 3. Crear el esquema en NeonDB

```bash
# En ambiente de desarrollo
python fase2_warehouse/create_schema.py development

# En producción (cuando esté listo)
python fase2_warehouse/create_schema.py production
```

Este script:
- Conecta a NeonDB
- Ejecuta el DDL completo
- Crea todas las tablas dimensionales y de hechos
- Crea índices para optimización de queries

### 4. Ejecutar la carga completa (ETL)

```bash
# En ambiente de desarrollo
python fase2_warehouse/etl_warehouse.py development

# En producción
python fase2_warehouse/etl_warehouse.py production
```

El ETL ejecuta los siguientes pasos:

1. **Extracción**: Lee datos de Delta Lake (capa Bronze)
2. **Transformación**:
   - Limpieza de datos (manejo de nulos)
   - Normalización de tipos de datos
   - Desanidado de precios (outcomePrices → price_yes, price_no)
   - Parseo de campos JSON
3. **Carga**:
   - dim_time (con todas las fechas del rango)
   - dim_series
   - dim_tag (con jerarquía)
   - dim_event
   - dim_market
   - bridge_market_tag
   - fact_market_metrics

## 📊 Características del Data Warehouse

### Integridad de Datos

✅ **Limpieza**:
- Manejo de valores NULL
- Conversión de `nan` a `None`
- Limpieza de strings vacíos

✅ **Normalización**:
- Conversión de tipos de datos apropiados
- Fechas en formato TIMESTAMP
- Numéricos en NUMERIC con precisión adecuada

✅ **Desanidado**:
- Array `outcomePrices` → `outcome_price_yes`, `outcome_price_no`
- Array `outcomes` → JSONB estructurado
- Campos JSON parseados correctamente

### Optimización para Consultas Analíticas

✅ **Índices**:
- Índices en claves primarias y foráneas
- Índices en columnas de filtrado frecuente (fechas, categorías)
- Índices compuestos para queries comunes

✅ **Particionamiento lógico**:
- Dimensión de tiempo completa pregenerada
- SCD Type 2 en dimensiones principales

✅ **Star Schema**:
- Queries optimizadas con joins directos
- Tabla puente para relaciones many-to-many
- Desnormalización controlada en tabla de hechos

## 📈 Consultas Analíticas de Ejemplo

### Volumen total por categoría
```sql
SELECT 
    dm.category,
    SUM(fmm.volume) as total_volume,
    COUNT(DISTINCT dm.market_key) as num_markets
FROM fact_market_metrics fmm
JOIN dim_market dm ON fmm.market_key = dm.market_key
WHERE dm.is_current = TRUE
GROUP BY dm.category
ORDER BY total_volume DESC;
```

### Evolución de liquidez en el tiempo
```sql
SELECT 
    dt.date_value,
    dt.year,
    dt.month_name,
    SUM(fmm.liquidity) as total_liquidity,
    AVG(fmm.liquidity) as avg_liquidity
FROM fact_market_metrics fmm
JOIN dim_time dt ON fmm.snapshot_date_key = dt.time_key
GROUP BY dt.date_value, dt.year, dt.month_name
ORDER BY dt.date_value;
```

### Top mercados por volumen
```sql
SELECT 
    dm.question,
    dm.category,
    fmm.volume,
    fmm.liquidity,
    fmm.outcome_price_yes,
    fmm.outcome_price_no
FROM fact_market_metrics fmm
JOIN dim_market dm ON fmm.market_key = dm.market_key
JOIN dim_time dt ON fmm.snapshot_date_key = dt.time_key
WHERE dt.date_value = CURRENT_DATE
  AND dm.is_current = TRUE
ORDER BY fmm.volume DESC
LIMIT 10;
```

### Análisis por jerarquía de tags
```sql
SELECT 
    dt.label,
    dt.level,
    dt.path,
    COUNT(DISTINCT bmt.market_key) as num_markets,
    SUM(fmm.volume) as total_volume
FROM dim_tag dt
JOIN bridge_market_tag bmt ON dt.tag_key = bmt.tag_key
JOIN fact_market_metrics fmm ON bmt.market_key = fmm.market_key
WHERE dt.is_current = TRUE
GROUP BY dt.tag_key, dt.label, dt.level, dt.path
ORDER BY dt.level, total_volume DESC;
```

## 🔧 Mantenimiento

### Actualización incremental

Para actualizaciones futuras, el ETL soporta:
- **UPSERT**: ON CONFLICT DO UPDATE en dimensiones
- **SCD Type 2**: Versionado histórico en dimensiones principales
- **Idempotencia**: Puede ejecutarse múltiples veces sin duplicar datos

### Logs

Los logs del ETL se guardan en:
```
logs/etl_warehouse_YYYYMMDD_HHMMSS.log
```

## 📝 Notas Técnicas

- **PostgreSQL Version**: 17
- **Region**: AWS US East 1
- **Connection Pooling**: Habilitado
- **SSL**: Requerido
- **Transacciones**: Habilitadas (autocommit=False)
- **Batch Insert**: Usando `execute_values` para eficiencia

## ✅ Validación

Después de la carga, validar:

```sql
-- Contar registros en cada tabla
SELECT 'dim_time' as tabla, COUNT(*) as registros FROM dim_time
UNION ALL
SELECT 'dim_series', COUNT(*) FROM dim_series
UNION ALL
SELECT 'dim_tag', COUNT(*) FROM dim_tag
UNION ALL
SELECT 'dim_event', COUNT(*) FROM dim_event
UNION ALL
SELECT 'dim_market', COUNT(*) FROM dim_market
UNION ALL
SELECT 'bridge_market_tag', COUNT(*) FROM bridge_market_tag
UNION ALL
SELECT 'fact_market_metrics', COUNT(*) FROM fact_market_metrics;

-- Verificar integridad referencial
SELECT 
    COUNT(*) as total_facts,
    COUNT(DISTINCT market_key) as unique_markets,
    COUNT(DISTINCT snapshot_date_key) as unique_dates
FROM fact_market_metrics;
```

## 🎯 Próximos Pasos

1. Ejecutar queries analíticas
2. Crear vistas materializadas para reports frecuentes
3. Implementar actualizaciones incrementales diarias
4. Configurar monitoring y alertas
5. Documentar KPIs y métricas de negocio
