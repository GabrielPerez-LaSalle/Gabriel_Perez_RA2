"""
Modelos Pydantic para la API
Esquemas de respuesta y validación de datos
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal

# ============================================================
# MODELOS BASE
# ============================================================

class ResponseBase(BaseModel):
    """Modelo base para respuestas"""
    success: bool = True
    message: Optional[str] = None

# ============================================================
# MODELOS DE MERCADO
# ============================================================

class MarketBasic(BaseModel):
    """Información básica de un mercado"""
    market_id: str
    question: str
    slug: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    active: Optional[bool] = None
    closed: Optional[bool] = None
    
    class Config:
        from_attributes = True

class MarketMetrics(BaseModel):
    """Métricas de un mercado"""
    volume: Optional[Decimal] = Field(None, description="Volumen total")
    volume_24hr: Optional[Decimal] = Field(None, description="Volumen últimas 24 horas")
    liquidity: Optional[Decimal] = Field(None, description="Liquidez actual")
    outcome_price_yes: Optional[Decimal] = Field(None, description="Probabilidad implícita de Yes")
    outcome_price_no: Optional[Decimal] = Field(None, description="Probabilidad implícita de No")
    last_trade_price: Optional[Decimal] = Field(None, description="Precio del último trade")
    spread: Optional[Decimal] = Field(None, description="Spread bid-ask")
    
    class Config:
        from_attributes = True

class MarketDetail(MarketBasic):
    """Detalles completos de un mercado"""
    description: Optional[str] = None
    market_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    closed_time: Optional[datetime] = None
    image: Optional[str] = None
    outcomes: Optional[Any] = None
    
    # Métricas actuales
    metrics: Optional[MarketMetrics] = None
    
    class Config:
        from_attributes = True

class MarketTopVolume(BaseModel):
    """Mercado con métricas de volumen (para top rankings)"""
    market_id: str
    question: str
    category: Optional[str] = None
    volume: Decimal
    volume_24hr: Optional[Decimal] = None
    liquidity: Optional[Decimal] = None
    outcome_price_yes: Optional[Decimal] = None
    
    class Config:
        from_attributes = True

class MarketClosingSoon(BaseModel):
    """Mercado que está por cerrar"""
    market_id: str
    question: str
    slug: str
    category: Optional[str] = None
    end_date: datetime
    hours_until_close: float
    volume: Optional[Decimal] = None
    outcome_price_yes: Optional[Decimal] = None
    active: Optional[bool] = None
    
    class Config:
        from_attributes = True

# ============================================================
# MODELOS DE EVENTO
# ============================================================

class EventBasic(BaseModel):
    """Información básica de un evento"""
    event_id: int
    title: str
    slug: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    active: Optional[bool] = None
    closed: Optional[bool] = None
    
    class Config:
        from_attributes = True

class EventDetail(EventBasic):
    """Detalles completos de un evento"""
    description: Optional[str] = None
    ticker: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    closed_time: Optional[datetime] = None
    image: Optional[str] = None
    series_slug: Optional[str] = None
    featured: Optional[bool] = None
    
    class Config:
        from_attributes = True

# ============================================================
# MODELOS DE SERIE
# ============================================================

class SeriesBasic(BaseModel):
    """Información básica de una serie"""
    series_id: str
    title: str
    slug: str
    series_type: Optional[str] = None
    active: Optional[bool] = None
    
    class Config:
        from_attributes = True

class SeriesDetail(SeriesBasic):
    """Detalles completos de una serie"""
    description: Optional[str] = None
    image: Optional[str] = None
    recurrence: Optional[str] = None
    featured: Optional[bool] = None
    start_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SeriesWithMarkets(SeriesDetail):
    """Serie con sus mercados"""
    markets: List[MarketBasic] = []
    total_markets: int = 0
    
    class Config:
        from_attributes = True

# ============================================================
# MODELOS DE TAG
# ============================================================

class TagBasic(BaseModel):
    """Información básica de un tag"""
    tag_id: str
    label: str
    slug: str
    level: Optional[int] = None
    
    class Config:
        from_attributes = True

class TagDetail(TagBasic):
    """Detalles completos de un tag"""
    parent_tag_id: Optional[str] = None
    path: Optional[str] = None
    is_carousel: Optional[bool] = None
    
    class Config:
        from_attributes = True

class TagWithMarkets(TagDetail):
    """Tag con mercados relacionados"""
    markets: List[MarketBasic] = []
    total_markets: int = 0
    
    class Config:
        from_attributes = True

# ============================================================
# MODELOS DE ANALYTICS
# ============================================================

class CategoryStats(BaseModel):
    """Estadísticas por categoría"""
    category: str
    total_markets: int
    active_markets: int
    total_volume: Decimal
    avg_volume: Decimal
    total_liquidity: Decimal
    
    class Config:
        from_attributes = True

class VolumeTrend(BaseModel):
    """Tendencia de volumen por fecha"""
    date: str
    total_volume: Decimal
    total_markets: int
    avg_volume_per_market: Decimal
    
    class Config:
        from_attributes = True

class ProbabilityEvolution(BaseModel):
    """Evolución de probabilidad de una serie"""
    date: str
    avg_probability_yes: Optional[Decimal] = None
    market_count: int
    
    class Config:
        from_attributes = True

# ============================================================
# MODELOS DE RESPUESTA PAGINADA
# ============================================================

class PaginatedResponse(BaseModel):
    """Respuesta con paginación"""
    data: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        from_attributes = True

# ============================================================
# MODELOS DE HEALTH CHECK
# ============================================================

class HealthCheck(BaseModel):
    """Health check de la API"""
    status: str
    version: str
    database: str
    timestamp: datetime
    
    class Config:
        from_attributes = True
