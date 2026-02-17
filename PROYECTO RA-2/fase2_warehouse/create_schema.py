"""
Script para crear el esquema del Data Warehouse en NeonDB
Ejecuta el DDL para crear todas las tablas dimensionales y de hechos
"""
import psycopg2
from neondb_config import get_connection_string, DEFAULT_ENVIRONMENT
import os
import sys

def create_schema(environment=DEFAULT_ENVIRONMENT):
    """
    Crea el esquema del Data Warehouse en NeonDB
    
    Args:
        environment: 'development' o 'production'
    """
    print(f"\n{'='*60}")
    print(f"CREANDO ESQUEMA DATA WAREHOUSE EN NEONDB")
    print(f"Ambiente: {environment.upper()}")
    print(f"{'='*60}\n")
    
    # Leer archivo SQL
    sql_file = os.path.join(os.path.dirname(__file__), 'schema_ddl.sql')
    
    if not os.path.exists(sql_file):
        print(f"❌ ERROR: No se encontró el archivo {sql_file}")
        return False
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Conectar a NeonDB
    conn = None
    try:
        print("🔌 Conectando a NeonDB...")
        conn = psycopg2.connect(get_connection_string(environment))
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Conexión establecida")
        print(f"\n📝 Ejecutando script DDL...")
        
        # Ejecutar el script SQL
        cursor.execute(sql_script)
        
        print("✅ Esquema creado exitosamente")
        
        # Verificar tablas creadas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        print(f"\n📊 Tablas creadas ({len(tables)}):")
        for table in tables:
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = '{table[0]}'
            """)
            column_count = cursor.fetchone()[0]
            print(f"  ✓ {table[0]}: {column_count} columnas")
        
        cursor.close()
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ ERROR de PostgreSQL:")
        print(f"   Código: {e.pgcode}")
        print(f"   Mensaje: {e.pgerror}")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False
        
    finally:
        if conn:
            conn.close()
            print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    # Permitir especificar ambiente desde línea de comandos
    environment = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ENVIRONMENT
    
    if environment not in ['development', 'production']:
        print("❌ Ambiente inválido. Use 'development' o 'production'")
        sys.exit(1)
    
    success = create_schema(environment)
    sys.exit(0 if success else 1)
