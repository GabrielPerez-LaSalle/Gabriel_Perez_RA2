"""
Polymarket Data Warehouse API
FastAPI application para exposición de datos
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from config import settings
from database import test_connection
from routers import markets, events, series, tags, analytics

# Crear instancia de FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(markets.router)
app.include_router(events.router)
app.include_router(series.router)
app.include_router(tags.router)
app.include_router(analytics.router)

# ============================================================
# ENDPOINT RAÍZ Y HEALTH CHECK
# ============================================================

@app.get("/")
async def root():
    """
    Endpoint raíz - Información de la API
    """
    return {
        "message": "Polymarket Data Warehouse API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "markets": "/markets/",
            "events": "/events/",
            "series": "/series/",
            "tags": "/tags/",
            "analytics": "/analytics/"
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check de la API
    
    Verifica el estado de la API y la conexión a la base de datos.
    """
    db_status = "healthy" if test_connection() else "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.API_VERSION,
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================
# STARTUP Y SHUTDOWN EVENTS
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Ejecutar al iniciar la aplicación"""
    print(f"🚀 Starting {settings.API_TITLE} v{settings.API_VERSION}")
    print(f"📊 Database: {settings.DB_HOST}")
    
    # Verificar conexión a DB
    if test_connection():
        print("✅ Database connection successful")
    else:
        print("⚠️  Database connection failed")

@app.on_event("shutdown")
async def shutdown_event():
    """Ejecutar al cerrar la aplicación"""
    print("👋 Shutting down API")

# ============================================================
# EJECUTAR APLICACIÓN
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
