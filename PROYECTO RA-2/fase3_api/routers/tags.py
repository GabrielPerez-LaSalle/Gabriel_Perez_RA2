"""
Router: Tags
Endpoints relacionados con tags y categorización
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from models import TagBasic, TagDetail, TagWithMarkets, MarketBasic
from database import execute_query, execute_single_query

router = APIRouter(
    prefix="/tags",
    tags=["Tags"],
    responses={404: {"description": "Not found"}},
)

@router.get("/search", response_model=List[TagBasic])
async def search_tags(
    name: str = Query(..., min_length=2, description="Término de búsqueda (ej: 'crypto', 'sports')"),
    limit: int = Query(default=20, ge=1, le=100, description="Número de resultados")
):
    """
    Busca tags por nombre
    
    Realiza una búsqueda case-insensitive en los campos 'label' y 'slug' de los tags.
    Útil para encontrar categorías específicas (ej: crypto, politics, sports).
    """
    
    query = """
    SELECT 
        t.tag_id,
        t.label,
        t.slug,
        t.level
    FROM dim_tag t
    WHERE t.is_current = TRUE
        AND (t.label ILIKE %s OR t.slug ILIKE %s)
    ORDER BY 
        CASE WHEN t.label ILIKE %s THEN 0 ELSE 1 END,
        t.level ASC,
        t.label ASC
    LIMIT %s
    """
    
    search_pattern = f"%{name}%"
    exact_pattern = f"{name}%"
    results = execute_query(query, (search_pattern, search_pattern, exact_pattern, limit))
    
    if not results:
        return []
    
    return [dict(row) for row in results]

@router.get("/{tag_id}", response_model=TagDetail)
async def get_tag_detail(tag_id: str):
    """
    Obtiene los detalles completos de un tag específico
    
    Incluye información del tag, jerarquía y metadatos.
    """
    
    query = """
    SELECT 
        t.tag_id,
        t.label,
        t.slug,
        t.parent_tag_id,
        t.level,
        t.path,
        t.is_carousel
    FROM dim_tag t
    WHERE t.tag_id = %s
        AND t.is_current = TRUE
    """
    
    result = execute_single_query(query, (tag_id,))
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Tag {tag_id} not found")
    
    return dict(result)

@router.get("/{tag_id}/markets", response_model=TagWithMarkets)
async def get_tag_markets(
    tag_id: str,
    active_only: bool = Query(default=True, description="Solo mercados activos"),
    limit: int = Query(default=50, ge=1, le=200, description="Número de mercados a retornar")
):
    """
    Obtiene todos los mercados relacionados con un tag específico
    
    Retorna los detalles del tag junto con todos los mercados que están etiquetados con él.
    Útil para explorar todos los mercados de una categoría específica (ej: todos los mercados de crypto).
    """
    
    # Primero obtener el tag
    tag_query = """
    SELECT 
        t.tag_id,
        t.label,
        t.slug,
        t.parent_tag_id,
        t.level,
        t.path,
        t.is_carousel
    FROM dim_tag t
    WHERE t.tag_id = %s
        AND t.is_current = TRUE
    """
    
    tag_result = execute_single_query(tag_query, (tag_id,))
    
    if not tag_result:
        raise HTTPException(status_code=404, detail=f"Tag {tag_id} not found")
    
    tag_data = dict(tag_result)
    
    # Ahora obtener los mercados del tag
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
    INNER JOIN bridge_market_tag bmt ON m.market_key = bmt.market_key
    INNER JOIN dim_tag t ON bmt.tag_key = t.tag_key
    WHERE t.tag_id = %s
        AND t.is_current = TRUE
        AND m.is_current = TRUE
    """
    
    params = [tag_id]
    
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
    INNER JOIN bridge_market_tag bmt ON m.market_key = bmt.market_key
    INNER JOIN dim_tag t ON bmt.tag_key = t.tag_key
    WHERE t.tag_id = %s
        AND t.is_current = TRUE
        AND m.is_current = TRUE
    """
    
    count_params = [tag_id]
    if active_only:
        count_query += " AND m.active = TRUE"
    
    count_result = execute_single_query(count_query, tuple(count_params))
    total_markets = count_result['total'] if count_result else 0
    
    # Construir respuesta
    tag_data['markets'] = [dict(row) for row in markets_results] if markets_results else []
    tag_data['total_markets'] = total_markets
    
    return tag_data

@router.get("/", response_model=List[TagBasic])
async def get_tags(
    level: Optional[int] = Query(default=None, ge=1, le=10, description="Filtrar por nivel jerárquico"),
    limit: int = Query(default=100, ge=1, le=500, description="Número de resultados")
):
    """
    Obtiene lista de tags
    
    Retorna todos los tags disponibles con opción de filtrar por nivel jerárquico.
    Level 1 = tags de primer nivel (raíz), Level 2 = tags hijos, etc.
    """
    
    query = """
    SELECT 
        t.tag_id,
        t.label,
        t.slug,
        t.level
    FROM dim_tag t
    WHERE t.is_current = TRUE
    """
    
    params = []
    
    if level is not None:
        query += " AND t.level = %s"
        params.append(level)
    
    query += """
    ORDER BY t.level ASC, t.label ASC
    LIMIT %s
    """
    params.append(limit)
    
    results = execute_query(query, tuple(params))
    
    if not results:
        return []
    
    return [dict(row) for row in results]

@router.get("/hierarchy/{tag_id}/children", response_model=List[TagBasic])
async def get_tag_children(tag_id: str):
    """
    Obtiene los tags hijos de un tag específico
    
    Retorna todos los tags que tienen como padre el tag especificado.
    Útil para navegar la jerarquía de tags.
    """
    
    # Verificar que el tag existe
    tag_check = execute_single_query(
        "SELECT tag_id FROM dim_tag WHERE tag_id = %s AND is_current = TRUE",
        (tag_id,)
    )
    
    if not tag_check:
        raise HTTPException(status_code=404, detail=f"Tag {tag_id} not found")
    
    query = """
    SELECT 
        t.tag_id,
        t.label,
        t.slug,
        t.level
    FROM dim_tag t
    WHERE t.parent_tag_id = %s
        AND t.is_current = TRUE
    ORDER BY t.label ASC
    """
    
    results = execute_query(query, (tag_id,))
    
    if not results:
        return []
    
    return [dict(row) for row in results]
