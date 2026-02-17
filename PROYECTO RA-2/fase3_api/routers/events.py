"""
Router: Events
Endpoints relacionados con eventos
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta

from models import EventBasic, EventDetail
from database import execute_query, execute_single_query

router = APIRouter(
    prefix="/events",
    tags=["Events"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{event_id}", response_model=EventDetail)
async def get_event_detail(event_id: int):
    """
    Obtiene los detalles completos de un evento específico
    
    Incluye información del evento, categorización, fechas y metadatos.
    """
    
    query = """
    SELECT 
        e.event_id,
        e.title,
        e.slug,
        e.description,
        e.category,
        e.subcategory,
        e.ticker,
        e.start_date,
        e.end_date,
        e.closed_time,
        e.image,
        e.series_slug,
        e.active,
        e.closed,
        e.featured
    FROM dim_event e
    WHERE e.event_id = %s
        AND e.is_current = TRUE
    """
    
    result = execute_single_query(query, (event_id,))
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    
    return dict(result)

@router.get("/", response_model=List[EventBasic])
async def get_events(
    category: Optional[str] = Query(default=None, description="Filtrar por categoría"),
    active_only: bool = Query(default=True, description="Solo eventos activos"),
    limit: int = Query(default=50, ge=1, le=200, description="Número de resultados"),
    offset: int = Query(default=0, ge=0, description="Offset para paginación")
):
    """
    Obtiene lista de eventos
    
    Retorna eventos con opción de filtrar por categoría y estado activo.
    Soporta paginación.
    """
    
    query = """
    SELECT 
        e.event_id,
        e.title,
        e.slug,
        e.category,
        e.subcategory,
        e.active,
        e.closed
    FROM dim_event e
    WHERE e.is_current = TRUE
    """
    
    params = []
    
    if category:
        query += " AND e.category = %s"
        params.append(category)
    
    if active_only:
        query += " AND e.active = TRUE"
    
    query += """
    ORDER BY e.created_at DESC
    LIMIT %s OFFSET %s
    """
    params.extend([limit, offset])
    
    results = execute_query(query, tuple(params))
    
    if not results:
        return []
    
    return [dict(row) for row in results]

@router.get("/closing-soon/list", response_model=List[EventBasic])
async def get_events_closing_soon(
    hours: int = Query(default=48, ge=1, le=168, description="Horas hasta el cierre"),
    limit: int = Query(default=20, ge=1, le=100, description="Número de resultados")
):
    """
    Obtiene eventos que están por cerrar
    
    Retorna eventos activos que finalizarán en las próximas N horas.
    Similar al endpoint de markets pero a nivel de evento.
    """
    
    now = datetime.now()
    future_time = now + timedelta(hours=hours)
    
    query = """
    SELECT 
        e.event_id,
        e.title,
        e.slug,
        e.category,
        e.subcategory,
        e.active,
        e.closed
    FROM dim_event e
    WHERE e.is_current = TRUE
        AND e.active = TRUE
        AND e.end_date IS NOT NULL
        AND e.end_date BETWEEN NOW() AND %s
    ORDER BY e.end_date ASC
    LIMIT %s
    """
    
    results = execute_query(query, (future_time, limit))
    
    if not results:
        return []
    
    return [dict(row) for row in results]

@router.get("/featured/list", response_model=List[EventBasic])
async def get_featured_events(
    limit: int = Query(default=10, ge=1, le=50, description="Número de resultados")
):
    """
    Obtiene eventos destacados (featured)
    
    Retorna eventos marcados como 'featured' que están activos.
    """
    
    query = """
    SELECT 
        e.event_id,
        e.title,
        e.slug,
        e.category,
        e.subcategory,
        e.active,
        e.closed
    FROM dim_event e
    WHERE e.is_current = TRUE
        AND e.featured = TRUE
        AND e.active = TRUE
    ORDER BY e.created_at DESC
    LIMIT %s
    """
    
    results = execute_query(query, (limit,))
    
    if not results:
        return []
    
    return [dict(row) for row in results]
