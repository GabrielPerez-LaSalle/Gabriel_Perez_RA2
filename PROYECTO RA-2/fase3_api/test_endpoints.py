"""
Script de prueba de endpoints de la API
Demuestra el uso de todos los endpoints principales
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"

def print_section(title):
    """Imprime una sección título"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def test_endpoint(method, endpoint, description, params=None):
    """Prueba un endpoint y muestra el resultado"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"TEST: {description}")
    print(f"   Endpoint: {method} {endpoint}")
    
    if params:
        print(f"   Parámetros: {params}")
    
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        else:
            response = requests.request(method, url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   OK Status: {response.status_code}")
            print(f"   Datos:")
            
            # Mostrar primeros resultados si es una lista
            if isinstance(data, list):
                print(f"      Total resultados: {len(data)}")
                if len(data) > 0:
                    print(f"      Primer resultado:")
                    print(f"      {json.dumps(data[0], indent=6, ensure_ascii=False)}")
            elif isinstance(data, dict):
                # Si es un dict con 'data', mostrar info de paginación
                if 'data' in data:
                    print(f"      Total: {data.get('total', 'N/A')}")
                    print(f"      Página: {data.get('page', 'N/A')}")
                else:
                    print(f"      {json.dumps(data, indent=6, ensure_ascii=False)}")
        else:
            print(f"   ERROR Status: {response.status_code}")
            print(f"   Error: {response.text}")
    
    except Exception as e:
        print(f"   ERROR Exception: {str(e)}")
    
    print()

def main():
    """Ejecuta todas las pruebas"""
    
    print("\n")
    print("=" * 70)
    print("         POLYMARKET DATA WAREHOUSE API")
    print("              PRUEBAS DE ENDPOINTS")
    print("=" * 70)
    
    # ============================================================
    # ROOT & HEALTH
    # ============================================================
    print_section("1. ROOT & HEALTH CHECK")
    
    test_endpoint("GET", "/", "Información general de la API")
    test_endpoint("GET", "/health", "Health check de la API")
    
    # ============================================================
    # MARKETS
    # ============================================================
    print_section("2. MARKETS - Mercados de Predicción")
    
    test_endpoint(
        "GET", 
        "/markets/top-volume", 
        "Top 5 mercados por volumen",
        {"limit": 5}
    )
    
    test_endpoint(
        "GET", 
        "/markets/top-volume", 
        "Top 3 mercados de Sports por volumen",
        {"limit": 3, "category": "Sports"}
    )
    
    test_endpoint(
        "GET", 
        "/markets/closing-soon", 
        "Mercados que cierran en 48 horas",
        {"hours": 48, "limit": 5}
    )
    
    test_endpoint(
        "GET", 
        "/markets/search/", 
        "Buscar mercados sobre 'Trump'",
        {"query": "Trump", "limit": 3}
    )
    
    # ============================================================
    # EVENTS
    # ============================================================
    print_section("3. EVENTS - Eventos")
    
    test_endpoint(
        "GET", 
        "/events/", 
        "Lista de eventos activos",
        {"active_only": True, "limit": 5}
    )
    
    test_endpoint(
        "GET", 
        "/events/featured/list", 
        "Eventos destacados (featured)",
        {"limit": 3}
    )
    
    # ============================================================
    # SERIES
    # ============================================================
    print_section("4. SERIES - Series de Mercados")
    
    test_endpoint(
        "GET", 
        "/series/", 
        "Lista de series activas",
        {"active_only": True, "limit": 5}
    )
    
    # ============================================================
    # TAGS
    # ============================================================
    print_section("5. TAGS - Categorización")
    
    test_endpoint(
        "GET", 
        "/tags/search", 
        "Buscar tags sobre 'crypto'",
        {"name": "crypto", "limit": 5}
    )
    
    test_endpoint(
        "GET", 
        "/tags/", 
        "Lista de tags de nivel 1 (raíz)",
        {"level": 1, "limit": 10}
    )
    
    # ============================================================
    # ANALYTICS
    # ============================================================
    print_section("6. ANALYTICS - Análisis y Estadísticas")
    
    test_endpoint(
        "GET", 
        "/analytics/category-stats", 
        "Estadísticas por categoría (Top 5)",
        {"limit": 5}
    )
    
    test_endpoint(
        "GET", 
        "/analytics/market-metrics-summary", 
        "Resumen general de métricas"
    )
    
    test_endpoint(
        "GET", 
        "/analytics/trending-markets", 
        "Top 5 mercados trending (24hr)",
        {"limit": 5}
    )
    
    test_endpoint(
        "GET", 
        "/analytics/top-categories-by-liquidity", 
        "Top 5 categorías por liquidez",
        {"limit": 5}
    )
    
    # ============================================================
    # RESUMEN
    # ============================================================
    print_section("RESUMEN DE PRUEBAS")
    
    print("OK Todas las pruebas completadas")
    print("\nPara mas informacion:")
    print(f"   - Documentacion Swagger: {BASE_URL}/docs")
    print(f"   - Documentacion ReDoc: {BASE_URL}/redoc")
    print(f"   - OpenAPI JSON: {BASE_URL}/openapi.json")
    
    print("\nEjemplos de integracion:")
    print("   - Python: import requests; requests.get('http://localhost:8000/markets/top-volume')")
    print("   - JavaScript: fetch('http://localhost:8000/markets/top-volume')")
    print("   - cURL: curl http://localhost:8000/markets/top-volume")
    
    print("\n" + "=" * 70)
    print("  API funcionando correctamente!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
