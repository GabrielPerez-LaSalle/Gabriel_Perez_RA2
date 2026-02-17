"""
Script de validación del Data Warehouse
Verifica integridad, calidad de datos y métricas básicas
"""
import psycopg2
from neondb_config import get_connection_string, DEFAULT_ENVIRONMENT
from tabulate import tabulate
import sys

class WarehouseValidator:
    """
    Validador de Data Warehouse
    """
    
    def __init__(self, environment=DEFAULT_ENVIRONMENT):
        self.environment = environment
        self.conn = None
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def connect(self):
        """Conectar a NeonDB"""
        try:
            self.conn = psycopg2.connect(get_connection_string(self.environment))
            return True
        except Exception as e:
            print(f"❌ Error al conectar: {str(e)}")
            return False
    
    def disconnect(self):
        """Desconectar"""
        if self.conn:
            self.conn.close()
    
    def run_query(self, query):
        """Ejecutar query y retornar resultados"""
        cursor = self.conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return results
    
    def test_table_counts(self):
        """Verificar que las tablas tengan datos"""
        print("\n📊 Validando conteo de registros...")
        
        query = """
            SELECT 'dim_time' as tabla, COUNT(*) as registros FROM dim_time
            UNION ALL
            SELECT 'dim_series', COUNT(*) FROM dim_series
            UNION ALL
            SELECT 'dim_tag', COUNT(*) FROM dim_tag
            UNION ALL
            SELECT 'dim_event', COUNT(*) FROM dim_event
            UNION ALL
            SELECT 'dim_market', COUNT(*) FROM dim_market
            UNION ALL
            SELECT 'bridge_market_tag', COUNT(*) FROM bridge_market_tag
            UNION ALL
            SELECT 'fact_market_metrics', COUNT(*) FROM fact_market_metrics
            ORDER BY tabla;
        """
        
        results = self.run_query(query)
        
        print(tabulate(results, headers=['Tabla', 'Registros'], tablefmt='grid'))
        
        for table, count in results:
            if count == 0:
                self.results['warnings'].append(f"Tabla {table} está vacía")
            else:
                self.results['passed'].append(f"✓ {table}: {count} registros")
    
    def test_referential_integrity(self):
        """Verificar integridad referencial"""
        print("\n🔗 Validando integridad referencial...")
        
        tests = [
            {
                'name': 'fact_market_metrics → dim_market',
                'query': """
                    SELECT COUNT(*) 
                    FROM fact_market_metrics fmm
                    LEFT JOIN dim_market dm ON fmm.market_key = dm.market_key
                    WHERE dm.market_key IS NULL
                """
            },
            {
                'name': 'fact_market_metrics → dim_time (snapshot)',
                'query': """
                    SELECT COUNT(*) 
                    FROM fact_market_metrics fmm
                    LEFT JOIN dim_time dt ON fmm.snapshot_date_key = dt.time_key
                    WHERE dt.time_key IS NULL
                """
            },
            {
                'name': 'bridge_market_tag → dim_market',
                'query': """
                    SELECT COUNT(*) 
                    FROM bridge_market_tag bmt
                    LEFT JOIN dim_market dm ON bmt.market_key = dm.market_key
                    WHERE dm.market_key IS NULL
                """
            },
            {
                'name': 'bridge_market_tag → dim_tag',
                'query': """
                    SELECT COUNT(*) 
                    FROM bridge_market_tag bmt
                    LEFT JOIN dim_tag dt ON bmt.tag_key = dt.tag_key
                    WHERE dt.tag_key IS NULL
                """
            }
        ]
        
        for test in tests:
            result = self.run_query(test['query'])[0][0]
            if result == 0:
                print(f"  ✅ {test['name']}: OK")
                self.results['passed'].append(f"✓ Integridad {test['name']}")
            else:
                print(f"  ❌ {test['name']}: {result} registros huérfanos")
                self.results['failed'].append(f"✗ Integridad {test['name']}: {result} huérfanos")
    
    def test_null_values(self):
        """Verificar valores nulos en campos críticos"""
        print("\n⚠️  Validando valores nulos en campos críticos...")
        
        tests = [
            {
                'name': 'dim_market.question',
                'query': "SELECT COUNT(*) FROM dim_market WHERE question IS NULL"
            },
            {
                'name': 'dim_event.title',
                'query': "SELECT COUNT(*) FROM dim_event WHERE title IS NULL"
            },
            {
                'name': 'fact_market_metrics.market_key',
                'query': "SELECT COUNT(*) FROM fact_market_metrics WHERE market_key IS NULL"
            },
            {
                'name': 'fact_market_metrics.snapshot_date_key',
                'query': "SELECT COUNT(*) FROM fact_market_metrics WHERE snapshot_date_key IS NULL"
            }
        ]
        
        for test in tests:
            result = self.run_query(test['query'])[0][0]
            if result == 0:
                print(f"  ✅ {test['name']}: Sin nulos")
                self.results['passed'].append(f"✓ No nulos en {test['name']}")
            else:
                print(f"  ❌ {test['name']}: {result} valores nulos")
                self.results['failed'].append(f"✗ {result} nulos en {test['name']}")
    
    def test_data_quality(self):
        """Validaciones de calidad de datos"""
        print("\n🎯 Validando calidad de datos...")
        
        # Verificar que los precios estén en rango [0, 1]
        query = """
            SELECT COUNT(*)
            FROM fact_market_metrics
            WHERE (outcome_price_yes IS NOT NULL AND (outcome_price_yes < 0 OR outcome_price_yes > 1))
               OR (outcome_price_no IS NOT NULL AND (outcome_price_no < 0 OR outcome_price_no > 1))
        """
        result = self.run_query(query)[0][0]
        
        if result == 0:
            print(f"  ✅ Precios en rango válido [0, 1]")
            self.results['passed'].append("✓ Precios en rango válido")
        else:
            print(f"  ⚠️  {result} registros con precios fuera de rango [0, 1]")
            self.results['warnings'].append(f"{result} precios fuera de rango")
        
        # Verificar que volume >= 0
        query = """
            SELECT COUNT(*)
            FROM fact_market_metrics
            WHERE volume IS NOT NULL AND volume < 0
        """
        result = self.run_query(query)[0][0]
        
        if result == 0:
            print(f"  ✅ Volumen no negativo")
            self.results['passed'].append("✓ Volumen no negativo")
        else:
            print(f"  ❌ {result} registros con volumen negativo")
            self.results['failed'].append(f"✗ {result} volúmenes negativos")
    
    def test_metrics_summary(self):
        """Mostrar métricas resumen"""
        print("\n📈 Métricas resumen del Data Warehouse...")
        
        # Total de mercados activos
        query = """
            SELECT 
                COUNT(CASE WHEN active = TRUE THEN 1 END) as activos,
                COUNT(CASE WHEN closed = TRUE THEN 1 END) as cerrados,
                COUNT(*) as total
            FROM dim_market
            WHERE is_current = TRUE
        """
        result = self.run_query(query)[0]
        print(f"\n  Mercados:")
        print(f"    - Activos: {result[0]}")
        print(f"    - Cerrados: {result[1]}")
        print(f"    - Total: {result[2]}")
        
        # Distribución por categoría
        query = """
            SELECT category, COUNT(*) as count
            FROM dim_market
            WHERE is_current = TRUE AND category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
            LIMIT 5
        """
        results = self.run_query(query)
        print(f"\n  Top 5 Categorías:")
        for cat, count in results:
            print(f"    - {cat}: {count} mercados")
        
        # Métricas de hechos
        query = """
            SELECT 
                COUNT(*) as total_facts,
                COUNT(DISTINCT market_key) as unique_markets,
                COUNT(DISTINCT snapshot_date_key) as unique_dates,
                SUM(volume) as total_volume,
                AVG(volume) as avg_volume,
                SUM(liquidity) as total_liquidity
            FROM fact_market_metrics
        """
        result = self.run_query(query)[0]
        print(f"\n  Tabla de Hechos:")
        print(f"    - Total registros: {result[0]}")
        print(f"    - Mercados únicos: {result[1]}")
        print(f"    - Fechas únicas: {result[2]}")
        print(f"    - Volumen total: ${result[3]:,.2f}" if result[3] else "    - Volumen total: N/A")
        print(f"    - Volumen promedio: ${result[4]:,.2f}" if result[4] else "    - Volumen promedio: N/A")
        print(f"    - Liquidez total: ${result[5]:,.2f}" if result[5] else "    - Liquidez total: N/A")
    
    def run_all_validations(self):
        """Ejecutar todas las validaciones"""
        print("\n" + "="*60)
        print(f"VALIDACIÓN DEL DATA WAREHOUSE ({self.environment.upper()})")
        print("="*60)
        
        if not self.connect():
            return False
        
        try:
            self.test_table_counts()
            self.test_referential_integrity()
            self.test_null_values()
            self.test_data_quality()
            self.test_metrics_summary()
            
            # Resumen final
            print("\n" + "="*60)
            print("RESUMEN DE VALIDACIÓN")
            print("="*60)
            
            print(f"\n✅ Pruebas exitosas: {len(self.results['passed'])}")
            print(f"⚠️  Advertencias: {len(self.results['warnings'])}")
            print(f"❌ Pruebas fallidas: {len(self.results['failed'])}")
            
            if self.results['failed']:
                print("\n❌ FALLOS DETECTADOS:")
                for fail in self.results['failed']:
                    print(f"  {fail}")
            
            if self.results['warnings']:
                print("\n⚠️  ADVERTENCIAS:")
                for warn in self.results['warnings']:
                    print(f"  {warn}")
            
            print("\n" + "="*60)
            
            return len(self.results['failed']) == 0
            
        except Exception as e:
            print(f"\n❌ ERROR durante validación: {str(e)}")
            return False
            
        finally:
            self.disconnect()

def main():
    """Función principal"""
    environment = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ENVIRONMENT
    
    if environment not in ['development', 'production']:
        print("❌ Ambiente inválido. Use 'development' o 'production'")
        sys.exit(1)
    
    validator = WarehouseValidator(environment)
    success = validator.run_all_validations()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
