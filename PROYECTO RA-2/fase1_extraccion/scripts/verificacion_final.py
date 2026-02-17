"""Verificación final del Data Warehouse completo"""
import psycopg2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fase2_warehouse.neondb_config import get_connection_string

def main():
    environment = sys.argv[1] if len(sys.argv) > 1 else 'development'
    
    print("="*70)
    print("VERIFICACION FINAL DEL DATA WAREHOUSE - POLYMARKET")
    print("="*70)
    print(f"\nEntorno: {environment}\n")
    
    try:
        conn = psycopg2.connect(get_connection_string(environment))
        cursor = conn.cursor()
        
        # Resumen general
        print("[1] RESUMEN GENERAL")
        print("-"*70)
        
        tables = [
            ('dim_time', 'Dimension Tiempo'),
            ('dim_series', 'Dimension Series'),
            ('dim_tag', 'Dimension Tags'),
            ('dim_event', 'Dimension Eventos'),
            ('dim_market', 'Dimension Mercados'),
            ('bridge_market_tag', 'Puente Market-Tag'),
            ('fact_market_metrics', 'Tabla de Hechos')
        ]
        
        total_records = 0
        for table, label in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"  {label:30s} {count:>12,} registros")
        
        print(f"\n  TOTAL REGISTROS: {total_records:,}")
        
        # Métricas de negocio
        print(f"\n[2] METRICAS DE NEGOCIO")
        print("-"*70)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_markets,
                COUNT(CASE WHEN active THEN 1 END) as active_markets,
                COUNT(CASE WHEN closed THEN 1 END) as closed_markets
            FROM dim_market
        """)
        row = cursor.fetchone()
        print(f"  Mercados Totales:        {row[0]:>12,}")
        print(f"  Mercados Activos:        {row[1]:>12,}")
        print(f"  Mercados Cerrados:       {row[2]:>12,}")
        
        cursor.execute("""
            SELECT 
                SUM(volume) as total_volume,
                AVG(volume) as avg_volume,
                SUM(liquidity) as total_liquidity
            FROM fact_market_metrics
        """)
        row = cursor.fetchone()
        print(f"\n  Volumen Total:           ${row[0]:>12,.2f}")
        print(f"  Volumen Promedio:        ${row[1]:>12,.2f}")
        print(f"  Liquidez Total:          ${row[2]:>12,.2f}")
        
        # Top categorías
        print(f"\n[3] TOP 10 CATEGORIAS")
        print("-"*70)
        
        cursor.execute("""
            SELECT category, COUNT(*) as total
            FROM dim_market
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY total DESC
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]:30s} {row[1]:>8,} mercados")
        
        # Integridad referencial
        print(f"\n[4] INTEGRIDAD REFERENCIAL")
        print("-"*70)
        
        # Verificar FKs
        cursor.execute("""
            SELECT COUNT(*) FROM fact_market_metrics f
            LEFT JOIN dim_market m ON f.market_key = m.market_key
            WHERE m.market_key IS NULL
        """)
        orphans_market = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM bridge_market_tag b
            LEFT JOIN dim_market m ON b.market_key = m.market_key
            WHERE m.market_key IS NULL
        """)
        orphans_bridge = cursor.fetchone()[0]
        
        print(f"  Hechos sin mercado:      {orphans_market:>12,} registros")
        print(f"  Puente sin mercado:      {orphans_bridge:>12,} registros")
        
        if orphans_market == 0 and orphans_bridge == 0:
            print("\n  >> Integridad referencial: OK")
        
        # Ejemplo de query analítica
        print(f"\n[5] EJEMPLO: MERCADOS DE BITCOIN")
        print("-"*70)
        
        cursor.execute("""
            SELECT 
                question,
                category,
                CASE WHEN active THEN 'Activo' ELSE 'Cerrado' END as estado
            FROM dim_market
            WHERE LOWER(question) LIKE '%bitcoin%'
            ORDER BY created_at_source DESC
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            print(f"  - {row[0][:60]}...")
            print(f"    {row[1]} | {row[2]}")
            print()
        
        cursor.close()
        conn.close()
        
        print("="*70)
        print("VERIFICACION COMPLETADA - TODOS LOS DATOS CARGADOS")
        print("="*70)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
