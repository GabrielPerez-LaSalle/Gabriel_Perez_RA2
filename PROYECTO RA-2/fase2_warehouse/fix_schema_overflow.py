"""Ajustar schema para soportar valores grandes en fee"""
import psycopg2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fase2_warehouse.neondb_config import get_connection_string, DEFAULT_ENVIRONMENT

def fix_schema(environment=DEFAULT_ENVIRONMENT):
    print(f"Ajustando schema en {environment}...\n")
    
    conn = psycopg2.connect(get_connection_string(environment))
    cursor = conn.cursor()
    
    try:
        # Cambiar fee a NUMERIC(30,10) para soportar valores hasta 10^20
        print("[1/1] Modificando columna fee...")
        cursor.execute("""
            ALTER TABLE fact_market_metrics 
            ALTER COLUMN fee TYPE NUMERIC(30,10)
        """)
        conn.commit()
        print("  OK: fee ahora es NUMERIC(30,10)\n")
        
        # Verificar
        cursor.execute("""
            SELECT column_name, data_type, numeric_precision, numeric_scale
            FROM information_schema.columns
            WHERE table_name = 'fact_market_metrics' 
            AND column_name = 'fee'
        """)
        
        result = cursor.fetchone()
        print(f"Verificacion: {result[0]} = {result[1]}({result[2]},{result[3]})")
        
        print("\nOK: Schema ajustado correctamente")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    environment = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ENVIRONMENT
    success = fix_schema(environment)
    sys.exit(0 if success else 1)
