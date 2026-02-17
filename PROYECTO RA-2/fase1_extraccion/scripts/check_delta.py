"""
Script para verificar las tablas Delta Lake
"""
from delta_utils import DeltaLakeManager
import os

def main():
    manager = DeltaLakeManager()
    
    print("\n" + "="*60)
    print("TABLAS DELTA LAKE - RESUMEN")
    print("="*60)
    
    tables = manager.list_tables()
    
    if not tables:
        print("No se encontraron tablas Delta Lake")
        return
    
    for table_name in tables:
        print(f"\nTabla: {table_name.upper()}")
        print("-" * 60)
        
        # Obtener información de la tabla
        info = manager.get_table_info(table_name)
        
        if info:
            print(f"Versión actual: {info['version']}")
            print(f"Número de archivos: {len(info['files'])}")
            
            # Calcular tamaño total
            total_size = 0
            for file_path in info['files']:
                full_path = os.path.join(info['path'], file_path)
                if os.path.exists(full_path):
                    total_size += os.path.getsize(full_path)
            print(f"Tamaño total: {total_size / (1024*1024):.2f} MB")
            
            # Leer la tabla
            df = manager.read_delta_table(table_name)
            if df is not None:
                print(f"Registros: {len(df)}")
                print(f"Columnas: {len(df.columns)}")
                print(f"Columnas: {', '.join(df.columns[:10])}")
                if len(df.columns) > 10:
                    print(f"          ... y {len(df.columns) - 10} más")
        else:
            print("No se pudo obtener información de la tabla")
    
    print("\n" + "="*60)
    print("COMPARACIÓN CON ARCHIVOS JSON")
    print("="*60)
    
    # Comparar con archivos JSON
    data_dir = "data"
    if os.path.exists(data_dir):
        json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        
        if json_files:
            print("\nArchivos JSON encontrados:")
            for json_file in json_files:
                filepath = os.path.join(data_dir, json_file)
                size_mb = os.path.getsize(filepath) / (1024*1024)
                print(f"  {json_file}: {size_mb:.2f} MB")
        else:
            print("\nNo se encontraron archivos JSON")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
