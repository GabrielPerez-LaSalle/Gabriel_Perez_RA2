"""
Router: Markets
Endpoints relacionados con mercados de predicción
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import math

from models import (
    MarketTopVolume, 
    MarketClosingSoon, 
    MarketDetail,
    MarketBasic,
    MarketMetrics,
    PaginatedResponse
)
from database import execute_query, execute_single_query

router = APIRouter(
    prefix="/markets",
    tags=["Markets"],
    responses={404: {"description": "Not found"}},
)

@router.get("/top-volume", response_model=List[MarketTopVolume])
async def get_top_volume_markets(
    limit: int = Query(default=10, ge=1, le=100, description="Número de resultados"),
    category: Optional[str] = Query(default=None, description="Filtrar por categoría")
):
    """
    Obtiene los mercados con mayor volumen
    
    Retorna los N mercados con mayor volumen total, opcionalmente filtrados por categoría.
    Incluye métricas clave como volumen 24hr, liquidez y probabilidad actual.
    """
    
    query = """
    SELECT 
        m.market_id,
        m.question,
        m.category,
        COALESCE(f.volume, 0) as volume,
        COALESCE(f.volume_24hr, 0) as volume_24hr,
        COALESCE(f.liquidity, 0) as liquidity,
        f.outcome_price_yes
    FROM dim_market m
    LEFT JOIN fact_market_metrics f ON m.market_key = f.market_key
    WHERE m.is_current = TRUE
        AND m.active = TRUE
    """
    
    params = []
    if category:
        query += " AND m.category = %s"
        params.append(category)
    
    query += """
    ORDER BY COALESCE(f.volume, 0) DESC
    LIMIT %s
    """
    params.append(limit)
    
    results = execute_query(query, tuple(params))
    
    if not results:
        return []
    
    return [dict(row) for row in results]

@router.get("/closing-soon", response_model=List[MarketClosingSoon])
async def get_closing_soon_markets(
    hours: int = Query(default=48, ge=1, le=168, description="Horas hasta el cierre"),
    limit: int = Query(default=20, ge=1, le=100, description="Número de resultados")
):
    """
    Obtiene mercados que están por cerrar
    
    Retorna mercados activos que finalizarán en las próximas N horas.
    Útil para identificar oportunidades de trading de último momento.
    """
    
    now = datetime.now()
    future_time = now + timedelta(hours=hours)
    
    query = """
    SELECT 
        m.market_id,
        m.question,
        m.slug,
        m.category,
        m.end_date,
        EXTRACT(EPOCH FROM (m.end_date - NOW())) / 3600 as hours_until_close,
        COALESCE(f.volume, 0) as volume,
        f.outcome_price_yes,
        m.active
    FROM dim_market m
    LEFT JOIN fact_market_metrics f ON m.market_key = f.market_key
    WHERE m.is_current = TRUE
        AND m.active = TRUE
        AND m.end_date IS NOT NULL
        AND m.end_date BETWEEN NOW() AND %s
    ORDER BY m.end_date ASC
    LIMIT %s
    """
    
    results = execute_query(query, (future_time, limit))
    
    if not results:
        return []
    
    return [dict(row) for row in results]

@router.get("/{market_id}", response_model=MarketDetail)
async def get_market_detail(market_id: str):
    """
    Obtiene los detalles completos de un mercado específico
    
    Incluye información del mercado, configuración, fechas y métricas actuales.
    """
    
    query = """
    SELECT 
        m.market_id,
        m.question,
        m.slug,
        m.description,
        m.category,
        m.subcategory,
        m.market_type,
        m.active,
        m.closed,
        m.start_date,
        m.end_date,
        m.closed_time,
        m.image,
        m.outcomes,
        -- Métricas
        f.volume,
        f.volume_24hr,
        f.liquidity,
        f.outcome_price_yes,
        f.outcome_price_no,
        f.last_trade_price,
        f.spread
    FROM dim_market m
    LEFT JOIN fact_market_metrics f ON m.market_key = f.market_key
    WHERE m.market_id = %s
        AND m.is_current = TRUE
    """
    
    result = execute_single_query(query, (market_id,))
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Market {market_id} not found")
    
    # Convertir a dict y estructurar métricas
    market_data = dict(result)
    
    # Extraer métricas en un objeto separado
    metrics = MarketMetrics(
        volume=market_data.pop('volume', None),
        volume_24hr=market_data.pop('volume_24hr', None),
        liquidity=market_data.pop('liquidity', None),
        outcome_price_yes=market_data.pop('outcome_price_yes', None),
        outcome_price_no=market_data.pop('outcome_price_no', None),
        last_trade_price=market_data.pop('last_trade_price', None),
        spread=market_data.pop('spread', None)
    )
    
    market_data['metrics'] = metrics
    
    return market_data

@router.get("/search/", response_model=List[MarketBasic])
async def search_markets(
    query: str = Query(..., min_length=3, description="Término de búsqueda"),
    limit: int = Query(default=20, ge=1, le=100, description="Número de resultados")
):
    """
    Busca mercados por palabras clave en la pregunta
    
    Realiza una búsqueda case-insensitive en el campo 'question' de los mercados.
    """
    
    sql_query = """
    SELECT 
        m.market_id,
        m.question,
        m.slug,
        m.category,
        m.subcategory,
        m.active,
        m.closed
    FROM dim_market m
    WHERE m.is_current = TRUE
        AND m.question ILIKE %s
    ORDER BY 
        CASE WHEN m.active = TRUE THEN 0 ELSE 1 END,
        m.created_at DESC
    LIMIT %s
    """
    
    search_pattern = f"%{query}%"
    results = execute_query(sql_query, (search_pattern, limit))
    
    if not results:
        return []
    
    return [dict(row) for row in results]

@router.get("/category/{category}", response_model=List[MarketBasic])
async def get_markets_by_category(
    category: str,
    active_only: bool = Query(default=True, description="Solo mercados activos"),
    limit: int = Query(default=50, ge=1, le=200, description="Número de resultados"),
    offset: int = Query(default=0, ge=0, description="Offset para paginación")
):
    """
    Obtiene mercados de una categoría específica
    
    Retorna todos los mercados de una categoría, con opción de filtrar solo activos.
    Soporta paginación para manejar grandes volúmenes de datos.
    """
    
    query = """
    SELECT 
        m.market_id,
        m.question,
        m.slug,
        m.category,
        m.subcategory,
        m.active,
        m.closed
    FROM dim_market m
    WHERE m.is_current = TRUE
        AND m.category = %s
    """
    
    params = [category]
    
    if active_only:
        query += " AND m.active = TRUE"
    
    query += """
    ORDER BY m.created_at DESC
    LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    
    results = execute_query(query, tuple(params))
    
    if not results:
        return []
    
    return [dict(row) for row in results]
