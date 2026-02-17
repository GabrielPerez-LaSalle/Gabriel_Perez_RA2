"""
Router: Analytics
Endpoints para análisis y estadísticas agregadas
"""
from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime, timedelta

from models import CategoryStats, VolumeTrend
from database import execute_query

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/category-stats", response_model=List[CategoryStats])
async def get_category_statistics(
    limit: int = Query(default=20, ge=1, le=100, description="Número de categorías a retornar")
):
    """
    Obtiene estadísticas agregadas por categoría
    
    Retorna métricas clave por categoría: número de mercados, volumen total,
    volumen promedio y liquidez. Ordenado por volumen total descendente.
    Útil para identificar las categorías más activas.
    """
    
    query = """
    SELECT 
        m.category,
        COUNT(DISTINCT m.market_key) as total_markets,
        COUNT(DISTINCT CASE WHEN m.active = TRUE THEN m.market_key END) as active_markets,
        COALESCE(SUM(f.volume), 0) as total_volume,
        COALESCE(AVG(f.volume), 0) as avg_volume,
        COALESCE(SUM(f.liquidity), 0) as total_liquidity
    FROM dim_market m
    LEFT JOIN fact_market_metrics f ON m.market_key = f.market_key
    WHERE m.is_current = TRUE
        AND m.category IS NOT NULL
    GROUP BY m.category
    ORDER BY total_volume DESC
    LIMIT %s
    """
    
    results = execute_query(query, (limit,))
    
    if not results:
        return []
    
    return [dict(row) for row in results]

@router.get("/volume-trends", response_model=List[VolumeTrend])
async def get_volume_trends(
    days: int = Query(default=30, ge=1, le=365, description="Número de días de historial"),
    category: Optional[str] = Query(default=None, description="Filtrar por categoría")
):
    """
    Obtiene tendencias de volumen a lo largo del tiempo
    
    Retorna el volumen total diario, número de mercados y volumen promedio por mercado.
    Puede filtrarse por categoría específica.
    Útil para analizar la evolución de la actividad en la plataforma.
    """
    
    query = """
    SELECT 
        TO_CHAR(t.date_value, 'YYYY-MM-DD') as date,
        COALESCE(SUM(f.volume), 0) as total_volume,
        COUNT(DISTINCT f.market_key) as total_markets,
        CASE 
            WHEN COUNT(DISTINCT f.market_key) > 0 
            THEN COALESCE(SUM(f.volume), 0) / COUNT(DISTINCT f.market_key)
            ELSE 0 
        END as avg_volume_per_market
    FROM dim_time t
    LEFT JOIN fact_market_metrics f ON t.time_key = f.snapshot_date_key
    """
    
    params = []
    
    if category:
        query += """
        LEFT JOIN dim_market m ON f.market_key = m.market_key
        WHERE t.date_value >= CURRENT_DATE - INTERVAL '%s days'
            AND m.category = %s
            AND m.is_current = TRUE
        """
        params.extend([days, category])
    else:
        query += """
        WHERE t.date_value >= CURRENT_DATE - INTERVAL '%s days'
        """
        params.append(days)
    
    query += """
    GROUP BY t.date_value
    ORDER BY t.date_value ASC
    """
    
    results = execute_query(query, tuple(params))
    
    if not results:
        return []
    
    return [dict(row) for row in results]

@router.get("/top-categories-by-liquidity", response_model=List[dict])
async def get_top_categories_by_liquidity(
    limit: int = Query(default=10, ge=1, le=50, description="Número de categorías")
):
    """
    Obtiene las categorías con mayor liquidez total
    
    Retorna las categorías ordenadas por liquidez total, útil para identificar
    dónde se concentra el capital en la plataforma.
    """
    
    query = """
    SELECT 
        m.category,
        COALESCE(SUM(f.liquidity), 0) as total_liquidity,
        COUNT(DISTINCT m.market_key) as total_markets,
        COALESCE(AVG(f.liquidity), 0) as avg_liquidity
    FROM dim_market m
    LEFT JOIN fact_market_metrics f ON m.market_key = f.market_key
    WHERE m.is_current = TRUE
        AND m.category IS NOT NULL
    GROUP BY m.category
    ORDER BY total_liquidity DESC
    LIMIT %s
    """
    
    results = execute_query(query, (limit,))
    
    if not results:
        return []
    
    return [dict(row) for row in results]

@router.get("/market-metrics-summary", response_model=dict)
async def get_market_metrics_summary():
    """
    Obtiene un resumen general de métricas de mercado
    
    Retorna estadísticas globales: total de mercados, mercados activos,
    volumen total, liquidez total, y promedios. Útil para dashboard general.
    """
    
    query = """
    SELECT 
        COUNT(DISTINCT m.market_key) as total_markets,
        COUNT(DISTINCT CASE WHEN m.active = TRUE THEN m.market_key END) as active_markets,
        COUNT(DISTINCT CASE WHEN m.closed = TRUE THEN m.market_key END) as closed_markets,
        COALESCE(SUM(f.volume), 0) as total_volume,
        COALESCE(AVG(f.volume), 0) as avg_volume,
        COALESCE(SUM(f.liquidity), 0) as total_liquidity,
        COALESCE(AVG(f.liquidity), 0) as avg_liquidity,
        COUNT(DISTINCT m.category) as total_categories
    FROM dim_market m
    LEFT JOIN fact_market_metrics f ON m.market_key = f.market_key
    WHERE m.is_current = TRUE
    """
    
    result = execute_query(query)
    
    if not result or len(result) == 0:
        return {}
    
    return dict(result[0])

@router.get("/trending-markets", response_model=List[dict])
async def get_trending_markets(
    limit: int = Query(default=10, ge=1, le=50, description="Número de mercados")
):
    """
    Obtiene mercados con mayor actividad reciente (trending)
    
    Identifica mercados con mayor volumen en las últimas 24 horas,
    útil para descubrir qué predicciones están generando más interés.
    """
    
    query = """
    SELECT 
        m.market_id,
        m.question,
        m.category,
        COALESCE(f.volume_24hr, 0) as volume_24hr,
        COALESCE(f.volume, 0) as total_volume,
        f.outcome_price_yes,
        m.active
    FROM dim_market m
    LEFT JOIN fact_market_metrics f ON m.market_key = f.market_key
    WHERE m.is_current = TRUE
        AND m.active = TRUE
    ORDER BY COALESCE(f.volume_24hr, 0) DESC
    LIMIT %s
    """
    
    results = execute_query(query, (limit,))
    
    if not results:
        return []
    
    return [dict(row) for row in results]
