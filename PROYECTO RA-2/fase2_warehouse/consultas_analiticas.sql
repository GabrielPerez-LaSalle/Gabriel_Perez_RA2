-- ============================================================
-- CONSULTAS ANALÍTICAS DE EJEMPLO
-- Data Warehouse - NeonDB
-- ============================================================

-- ============================================================
-- 1. ANÁLISIS DE MERCADOS POR CATEGORÍA
-- ============================================================

-- Total de mercados y volumen por categoría
SELECT 
    dm.category,
    COUNT(DISTINCT dm.market_key) as total_mercados,
    COUNT(CASE WHEN dm.active = TRUE THEN 1 END) as activos,
    COUNT(CASE WHEN dm.closed = TRUE THEN 1 END) as cerrados
FROM dim_market dm
WHERE dm.is_current = TRUE
GROUP BY dm.category
ORDER BY total_mercados DESC
LIMIT 10;

-- ============================================================
-- 2. EVOLUCIÓN TEMPORAL
-- ============================================================

-- Mercados por mes y año
SELECT 
    dt.year,
    dt.month_name,
    COUNT(DISTINCT dm.market_key) as total_mercados
FROM dim_market dm
JOIN dim_time dt ON DATE(dm.created_at_source) = dt.date_value
WHERE dm.is_current = TRUE
GROUP BY dt.year, dt.month, dt.month_name
ORDER BY dt.year, dt.month;

-- ============================================================
-- 3. ANÁLISIS POR TAGS (JERARQUÍA)
-- ============================================================

-- Top tags por número de mercados
SELECT 
    dt.label,
    dt.slug,
    dt.level,
    dt.path,
    COUNT(DISTINCT bmt.market_key) as num_mercados
FROM dim_tag dt
LEFT JOIN bridge_market_tag bmt ON dt.tag_key = bmt.tag_key
WHERE dt.is_current = TRUE
GROUP BY dt.tag_key, dt.label, dt.slug, dt.level, dt.path
ORDER BY num_mercados DESC, dt.level
LIMIT 20;

-- ============================================================
-- 4. ANÁLISIS DE SERIES
-- ============================================================

-- Series más activas
SELECT 
    ds.title,
    ds.slug,
    ds.series_type,
    ds.recurrence,
    ds.active,
    ds.image
FROM dim_series ds
WHERE ds.is_current = TRUE
  AND ds.active = TRUE
ORDER BY ds.title
LIMIT 20;

-- ============================================================
-- 5. ANÁLISIS DE EVENTOS
-- ============================================================

-- Eventos por categoría
SELECT 
    de.category,
    COUNT(*) as total_eventos,
    COUNT(CASE WHEN de.active = TRUE THEN 1 END) as activos,
    COUNT(CASE WHEN de.closed = TRUE THEN 1 END) as cerrados,
    COUNT(CASE WHEN de.featured = TRUE THEN 1 END) as destacados
FROM dim_event de
WHERE de.is_current = TRUE
GROUP BY de.category
ORDER BY total_eventos DESC;

-- Eventos deportivos más recientes
SELECT 
    de.title,
    de.sport,
    de.category,
    de.game_id,
    de.game_status,
    de.event_date
FROM dim_event de
WHERE de.is_current = TRUE
  AND de.sport IS NOT NULL
ORDER BY de.event_date DESC NULLS LAST
LIMIT 20;

-- ============================================================
-- 6. ANÁLISIS DE MERCADOS DETALLADO
-- ============================================================

-- Mercados con más volumen (cuando se tenga la tabla de hechos)
/*
SELECT 
    dm.question,
    dm.category,
    dm.market_type,
    fmm.volume,
    fmm.liquidity,
    fmm.outcome_price_yes,
    fmm.outcome_price_no,
    fmm.open_interest
FROM fact_market_metrics fmm
JOIN dim_market dm ON fmm.market_key = dm.market_key
JOIN dim_time dt ON fmm.snapshot_date_key = dt.time_key
WHERE dt.date_value = CURRENT_DATE
  AND dm.is_current = TRUE
ORDER BY fmm.volume DESC NULLS LAST
LIMIT 10;
*/

-- Mercados activos por tipo
SELECT 
    dm.market_type,
    COUNT(*) as total,
    COUNT(CASE WHEN dm.active = TRUE THEN 1 END) as activos
FROM dim_market dm
WHERE dm.is_current = TRUE
  AND dm.market_type IS NOT NULL
GROUP BY dm.market_type
ORDER BY total DESC;

-- ============================================================
-- 7. ANÁLISIS TEMPORAL AVANZADO
-- ============================================================

-- Métricas por trimestre
SELECT 
    dt.year,
    dt.quarter,
    COUNT(DISTINCT dm.market_key) as mercados_creados
FROM dim_market dm
JOIN dim_time dt ON DATE(dm.created_at_source) = dt.date_value
WHERE dm.is_current = TRUE
GROUP BY dt.year, dt.quarter
ORDER BY dt.year, dt.quarter;

-- Distribución por día de la semana
SELECT 
    dt.day_name,
    dt.day_of_week,
    COUNT(DISTINCT dm.market_key) as mercados_creados,
    ROUND(COUNT(DISTINCT dm.market_key) * 100.0 / SUM(COUNT(DISTINCT dm.market_key)) OVER (), 2) as porcentaje
FROM dim_market dm
JOIN dim_time dt ON DATE(dm.created_at_source) = dt.date_value
WHERE dm.is_current = TRUE
GROUP BY dt.day_name, dt.day_of_week
ORDER BY dt.day_of_week;

-- ============================================================
-- 8. BÚSQUEDAS Y FILTROS
-- ============================================================

-- Buscar mercados por palabra clave en la pregunta
SELECT 
    dm.question,
    dm.category,
    dm.slug,
    dm.active,
    dm.closed
FROM dim_market dm
WHERE dm.is_current = TRUE
  AND LOWER(dm.question) LIKE '%bitcoin%'
ORDER BY dm.created_at_source DESC
LIMIT 20;

-- Mercados en categoría específica
SELECT 
    dm.question,
    dm.slug,
    dm.active,
    dm.closed,
    dm.created_at_source
FROM dim_market dm
WHERE dm.is_current = TRUE
  AND dm.category = 'Crypto'
ORDER BY dm.created_at_source DESC
LIMIT 20;

-- ============================================================
-- 9. ESTADÍSTICAS GENERALES
-- ============================================================

-- Resumen ejecutivo del Data Warehouse
SELECT 
    'Total Series' as metrica,
    COUNT(*) as valor
FROM dim_series
WHERE is_current = TRUE

UNION ALL

SELECT 
    'Total Tags',
    COUNT(*)
FROM dim_tag
WHERE is_current = TRUE

UNION ALL

SELECT 
    'Total Eventos',
    COUNT(*)
FROM dim_event
WHERE is_current = TRUE

UNION ALL

SELECT 
    'Total Mercados',
    COUNT(*)
FROM dim_market
WHERE is_current = TRUE

UNION ALL

SELECT 
    'Mercados Activos',
    COUNT(*)
FROM dim_market
WHERE is_current = TRUE AND active = TRUE

UNION ALL

SELECT 
    'Mercados Cerrados',
    COUNT(*)
FROM dim_market
WHERE is_current = TRUE AND closed = TRUE;

-- ============================================================
-- 10. ANÁLISIS DE OUTCOMES (Resultados)
-- ============================================================

-- Mercados por número de outcomes
SELECT 
    CASE 
        WHEN dm.outcomes IS NULL THEN 'Sin outcomes'
        WHEN jsonb_array_length(dm.outcomes::jsonb) = 2 THEN 'Binario (Yes/No)'
        ELSE 'Múltiple (' || jsonb_array_length(dm.outcomes::jsonb) || ')'
    END as tipo_outcome,
    COUNT(*) as total_mercados
FROM dim_market dm
WHERE dm.is_current = TRUE
GROUP BY tipo_outcome
ORDER BY total_mercados DESC;

-- ============================================================
-- 11. VISTAS MATERIALIZADAS SUGERIDAS
-- ============================================================

-- Vista: Resumen de mercados por categoría (para dashboards)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_market_summary_by_category AS
SELECT 
    dm.category,
    COUNT(*) as total_markets,
    COUNT(CASE WHEN dm.active THEN 1 END) as active_markets,
    COUNT(CASE WHEN dm.closed THEN 1 END) as closed_markets,
    COUNT(CASE WHEN dm.featured THEN 1 END) as featured_markets,
    MIN(dm.created_at_source) as first_market_date,
    MAX(dm.created_at_source) as last_market_date
FROM dim_market dm
WHERE dm.is_current = TRUE
GROUP BY dm.category;

-- Índice para la vista materializada
CREATE INDEX idx_mv_market_summary_category 
ON mv_market_summary_by_category(category);

-- Vista: Timeline de creación de mercados
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_market_timeline AS
SELECT 
    dt.date_value,
    dt.year,
    dt.month,
    dt.quarter,
    dt.day_name,
    COUNT(DISTINCT dm.market_key) as markets_created
FROM dim_market dm
JOIN dim_time dt ON DATE(dm.created_at_source) = dt.date_value
WHERE dm.is_current = TRUE
GROUP BY dt.date_value, dt.year, dt.month, dt.quarter, dt.day_name;

-- Para refrescar las vistas materializadas:
-- REFRESH MATERIALIZED VIEW mv_market_summary_by_category;
-- REFRESH MATERIALIZED VIEW mv_market_timeline;
