"""
Script de ejemplo para explorar el Data Warehouse en NeonDB
Demuestra cómo conectarse y ejecutar consultas analíticas
"""
import psycopg2
from fase2_warehouse.neondb_config import get_connection_string, DEFAULT_ENVIRONMENT
from tabulate import tabulate

def conectar_warehouse(environment=DEFAULT_ENVIRONMENT):
    """Conecta al Data Warehouse"""
    try:
        conn = psycopg2.connect(get_connection_string(environment))
        print(f"✓ Conectado a NeonDB ({environment})")
        return conn
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def ejecutar_query(conn, query, descripcion=""):
    """Ejecuta una query y muestra resultados"""
    if descripcion:
        print(f"\n{descripcion}")
        print("-" * 60)
    
    cursor = conn.cursor()
    cursor.execute(query)
    
    # Obtener nombres de columnas
    colnames = [desc[0] for desc in cursor.description]
    
    # Obtener resultados
    results = cursor.fetchall()
    
    # Mostrar tabla
    if results:
        print(tabulate(results, headers=colnames, tablefmt='grid'))
        print(f"\nTotal: {len(results)} registros")
    else:
        print("Sin resultados")
    
    cursor.close()
    return results

def main():
    """Función principal"""
    import sys
    
    environment = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ENVIRONMENT
    
    print("="*60)
    print("EXPLORADOR DEL DATA WAREHOUSE - POLYMARKET")
    print("="*60)
    
    # Conectar
    conn = conectar_warehouse(environment)
    if not conn:
        return
    
    try:
        # 1. Resumen general
        ejecutar_query(conn, """
            SELECT 'Series' as entidad, COUNT(*) as total FROM dim_series WHERE is_current = TRUE
            UNION ALL
            SELECT 'Tags', COUNT(*) FROM dim_tag WHERE is_current = TRUE
            UNION ALL
            SELECT 'Eventos', COUNT(*) FROM dim_event WHERE is_current = TRUE
            UNION ALL
            SELECT 'Mercados', COUNT(*) FROM dim_market WHERE is_current = TRUE
        """, "📊 RESUMEN GENERAL DEL DATA WAREHOUSE")
        
        # 2. Top 10 categorías
        ejecutar_query(conn, """
            SELECT 
                category as "Categoría",
                COUNT(*) as "Total Mercados",
                COUNT(CASE WHEN active THEN 1 END) as "Activos",
                COUNT(CASE WHEN closed THEN 1 END) as "Cerrados"
            FROM dim_market
            WHERE is_current = TRUE
            GROUP BY category
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """, "🏆 TOP 10 CATEGORÍAS DE MERCADOS")
        
        # 3. Top 10 series
        ejecutar_query(conn, """
            SELECT 
                title as "Serie",
                slug as "Slug",
                CASE WHEN active THEN 'Sí' ELSE 'No' END as "Activa"
            FROM dim_series
            WHERE is_current = TRUE
            ORDER BY title
            LIMIT 10
        """, "📁 TOP 10 SERIES")
        
        # 4. Tags más populares
        ejecutar_query(conn, """
            SELECT 
                label as "Tag",
                slug as "Slug",
                level as "Nivel",
                path as "Ruta Jerárquica"
            FROM dim_tag
            WHERE is_current = TRUE
            ORDER BY label
            LIMIT 10
        """, "🏷️  TOP 10 TAGS")
        
        # 5. Mercados recientes
        ejecutar_query(conn, """
            SELECT 
                LEFT(question, 60) || '...' as "Pregunta",
                category as "Categoría",
                CASE WHEN active THEN '✓' ELSE '✗' END as "Activo"
            FROM dim_market
            WHERE is_current = TRUE
            ORDER BY created_at_source DESC NULLS LAST
            LIMIT 10
        """, "🆕 MERCADOS MÁS RECIENTES")
        
        # 6. Distribución temporal
        ejecutar_query(conn, """
            SELECT 
                dt.year as "Año",
                dt.quarter as "Trimestre",
                COUNT(DISTINCT dm.market_key) as "Mercados Creados"
            FROM dim_market dm
            JOIN dim_time dt ON DATE(dm.created_at_source) = dt.date_value
            WHERE dm.is_current = TRUE
            GROUP BY dt.year, dt.quarter
            ORDER BY dt.year, dt.quarter
        """, "📅 DISTRIBUCIÓN TEMPORAL DE MERCADOS")
        
        # 7. Búsqueda de ejemplo: Bitcoin
        ejecutar_query(conn, """
            SELECT 
                LEFT(question, 70) as "Pregunta",
                category as "Categoría",
                CASE WHEN active THEN 'Activo' ELSE 'Cerrado' END as "Estado"
            FROM dim_market
            WHERE is_current = TRUE
              AND LOWER(question) LIKE '%bitcoin%'
            ORDER BY created_at_source DESC NULLS LAST
            LIMIT 5
        """, "🔍 BÚSQUEDA: Mercados sobre Bitcoin")
        
        print("\n" + "="*60)
        print("✓ Exploración completada")
        print("="*60)
        print("\nPara más consultas, ver: fase2_warehouse/consultas_analiticas.sql")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()
        print("\n✓ Conexión cerrada")

if __name__ == "__main__":
    main()
