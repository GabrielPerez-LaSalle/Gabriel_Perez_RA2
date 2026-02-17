"""
Router: Series
Endpoints relacionados con series de mercados
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from models import SeriesBasic, SeriesDetail, SeriesWithMarkets, MarketBasic, ProbabilityEvolution
from database import execute_query, execute_single_query

router = APIRouter(
    prefix="/series",
    tags=["Series"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{series_id}", response_model=SeriesDetail)
async def get_series_detail(series_id: str):
    """
    Obtiene los detalles completos de una serie específica
    
    Incluye información de la serie, tipo, recurrencia y metadatos.
    """
    
    query = """
    SELECT 
        s.series_id,
        s.title,
        s.slug,
        s.description,
        s.image,
        s.series_type,
        s.recurrence,
        s.active,
        s.featured,
        s.start_date
    FROM dim_series s
    WHERE s.series_id = %s
        AND s.is_current = TRUE
    """
    
    result = execute_single_query(query, (series_id,))
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")
    
    return dict(result)

@router.get("/{series_id}/markets", response_model=SeriesWithMarkets)
async def get_series_markets(
    series_id: str,
    active_only: bool = Query(default=True, description="Solo mercados activos"),
    limit: int = Query(default=50, ge=1, le=200, description="Número de mercados a retornar")
):
    """
    Obtiene una serie con sus mercados asociados
    
    Retorna los detalles de la serie junto con la lista de mercados que pertenecen a ella.
    Útil para analizar todas las predicciones dentro de una serie (ej: NBA Playoffs).
    """
    
    # Primero obtener la serie
    series_query = """
    SELECT 
        s.series_id,
        s.title,
        s.slug,
        s.description,
        s.image,
        s.series_type,
        s.recurrence,
        s.active,
        s.featured,
        s.start_date
    FROM dim_series s
    WHERE s.series_id = %s
        AND s.is_current = TRUE
    """
    
    series_result = execute_single_query(series_query, (series_id,))
    
    if not series_result:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")
    
    series_data = dict(series_result)
    
    # Ahora obtener los mercados de la serie
    markets_query = """
    SELECT 
        m.market_id,
        m.question,
        m.slug,
        m.category,
        m.subcategory,
        m.active,
        m.closed
    FROM dim_market m
    INNER JOIN fact_market_metrics f ON m.market_key = f.market_key
    INNER JOIN dim_event e ON f.event_key = e.event_key
    WHERE e.series_slug = (
        SELECT slug FROM dim_series WHERE series_id = %s AND is_current = TRUE
    )
    AND m.is_current = TRUE
    """
    
    params = [series_id]
    
    if active_only:
        markets_query += " AND m.active = TRUE"
    
    markets_query += """
    ORDER BY m.created_at DESC
    LIMIT %s
    """
    params.append(limit)
    
    markets_results = execute_query(markets_query, tuple(params))
    
    # Contar total de mercados
    count_query = """
    SELECT COUNT(DISTINCT m.market_key) as total
    FROM dim_market m
    INNER JOIN fact_market_metrics f ON m.market_key = f.market_key
    INNER JOIN dim_event e ON f.event_key = e.event_key
    WHERE e.series_slug = (
        SELECT slug FROM dim_series WHERE series_id = %s AND is_current = TRUE
    )
    AND m.is_current = TRUE
    """
    
    count_params = [series_id]
    if active_only:
        count_query += " AND m.active = TRUE"
    
    count_result = execute_single_query(count_query, tuple(count_params))
    total_markets = count_result['total'] if count_result else 0
    
    # Construir respuesta
    series_data['markets'] = [dict(row) for row in markets_results] if markets_results else []
    series_data['total_markets'] = total_markets
    
    return series_data

@router.get("/{series_id}/probability", response_model=List[ProbabilityEvolution])
async def get_series_probability_evolution(
    series_id: str,
    days: int = Query(default=30, ge=1, le=365, description="Número de días de historial")
):
    """
    Obtiene la evolución de probabilidad promedio de una serie
    
    Retorna la probabilidad implícita promedio (outcome_price_yes) de todos los mercados
    de la serie a lo largo del tiempo. Útil para analizar tendencias en series recurrentes.
    """
    
    # Verificar que la serie existe
    series_check = execute_single_query(
        "SELECT series_id FROM dim_series WHERE series_id = %s AND is_current = TRUE",
        (series_id,)
    )
    
    if not series_check:
        raise HTTPException(status_code=404, detail=f"Series {series_id} not found")
    
    query = """
    WITH series_markets AS (
        SELECT DISTINCT m.market_key
        FROM dim_market m
        INNER JOIN fact_market_metrics f ON m.market_key = f.market_key
        INNER JOIN dim_event e ON f.event_key = e.event_key
        WHERE e.series_slug = (
            SELECT slug FROM dim_series WHERE series_id = %s AND is_current = TRUE
        )
        AND m.is_current = TRUE
    )
    SELECT 
        TO_CHAR(t.date_value, 'YYYY-MM-DD') as date,
        AVG(f.outcome_price_yes) as avg_probability_yes,
        COUNT(DISTINCT f.market_key) as market_count
    FROM fact_market_metrics f
    INNER JOIN dim_time t ON f.snapshot_date_key = t.time_key
    WHERE f.market_key IN (SELECT market_key FROM series_markets)
        AND t.date_value >= CURRENT_DATE - INTERVAL '%s days'
    GROUP BY t.date_value
    ORDER BY t.date_value ASC
    """
    
    results = execute_query(query, (series_id, days))
    
    if not results:
        return []
    
    return [dict(row) for row in results]

@router.get("/", response_model=List[SeriesBasic])
async def get_series(
    active_only: bool = Query(default=True, description="Solo series activas"),
    limit: int = Query(default=50, ge=1, le=200, description="Número de resultados")
):
    """
    Obtiene lista de series
    
    Retorna todas las series disponibles con opción de filtrar solo activas.
    """
    
    query = """
    SELECT 
        s.series_id,
        s.title,
        s.slug,
        s.series_type,
        s.active
    FROM dim_series s
    WHERE s.is_current = TRUE
    """
    
    params = []
    
    if active_only:
        query += " AND s.active = TRUE"
    
    query += """
    ORDER BY s.created_at DESC
    LIMIT %s
    """
    params.append(limit)
    
    results = execute_query(query, tuple(params))
    
    if not results:
        return []
    
    return [dict(row) for row in results]
