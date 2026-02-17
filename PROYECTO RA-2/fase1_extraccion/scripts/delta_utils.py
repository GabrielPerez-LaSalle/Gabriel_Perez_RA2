"""
Utilidades para manejo de Delta Lake
Proporciona funciones para guardar y leer datos en formato Delta Lake
"""
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from deltalake import write_deltalake, DeltaTable
from datetime import datetime
from typing import List, Dict, Optional
import logging
import os
from config import DELTA_DIR, DELTA_CONFIG


class DeltaLakeManager:
    """Gestor de operaciones Delta Lake"""
    
    def __init__(self, base_path: str = DELTA_DIR):
        self.base_path = base_path
        self.logger = self._setup_logger()
        self._ensure_base_directory()
    
    def _setup_logger(self) -> logging.Logger:
        """Configurar el logger"""
        logger = logging.getLogger("DeltaLakeManager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler(f"logs/delta_lake_{datetime.now().strftime('%Y%m%d')}.log")
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _ensure_base_directory(self):
        """Asegurar que el directorio base existe"""
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            self.logger.info(f"Directorio Delta Lake creado: {self.base_path}")
    
    def save_to_delta(self, data: List[Dict], table_name: str, mode: str = "overwrite") -> bool:
        """
        Guarda datos en formato Delta Lake
        
        Args:
            data: Lista de diccionarios con los datos
            table_name: Nombre de la tabla Delta
            mode: Modo de escritura ('overwrite', 'append', 'error', 'ignore')
        
        Returns:
            True si se guardó exitosamente, False en caso contrario
        """
        try:
            if not data:
                self.logger.warning(f"No hay datos para guardar en {table_name}")
                return False
            
            # Convertir a DataFrame
            df = pd.DataFrame(data)
            
            # Agregar metadatos de extracción
            df['_extraction_timestamp'] = datetime.now()
            df['_extraction_date'] = datetime.now().date()
            
            # Ruta de la tabla Delta
            table_path = os.path.join(self.base_path, table_name)
            
            self.logger.info(f"Guardando {len(df)} registros en tabla Delta: {table_name}")
            
            # Escribir en formato Delta Lake
            write_deltalake(
                table_path,
                df,
                mode=mode,
                schema_mode="merge" if DELTA_CONFIG["enable_schema_evolution"] else "overwrite"
            )
            
            self.logger.info(f"Datos guardados exitosamente en {table_path}")
            
            # Obtener información de la tabla
            dt = DeltaTable(table_path)
            version = dt.version()
            
            self.logger.info(f"Tabla {table_name} - Versión: {version}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error al guardar datos en Delta Lake {table_name}: {str(e)}")
            return False
    
    def read_delta_table(self, table_name: str, version: Optional[int] = None) -> Optional[pd.DataFrame]:
        """
        Lee una tabla Delta Lake
        
        Args:
            table_name: Nombre de la tabla
            version: Versión específica a leer (None = última versión)
        
        Returns:
            DataFrame con los datos o None si hay error
        """
        try:
            table_path = os.path.join(self.base_path, table_name)
            
            if not os.path.exists(table_path):
                self.logger.error(f"Tabla Delta no existe: {table_path}")
                return None
            
            dt = DeltaTable(table_path)
            
            if version is not None:
                self.logger.info(f"Leyendo tabla {table_name} versión {version}")
                df = dt.load_version(version).to_pandas()
            else:
                self.logger.info(f"Leyendo última versión de tabla {table_name}")
                df = dt.to_pandas()
            
            self.logger.info(f"Leídos {len(df)} registros de {table_name}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error al leer tabla Delta {table_name}: {str(e)}")
            return None
    
    def get_table_info(self, table_name: str) -> Dict:
        """
        Obtiene información sobre una tabla Delta
        
        Args:
            table_name: Nombre de la tabla
        
        Returns:
            Diccionario con información de la tabla
        """
        try:
            table_path = os.path.join(self.base_path, table_name)
            
            if not os.path.exists(table_path):
                return {"error": f"Tabla no existe: {table_name}"}
            
            dt = DeltaTable(table_path)
            
            info = {
                "table_name": table_name,
                "path": table_path,
                "version": dt.version(),
                "files": dt.files(),
                "schema": dt.schema().to_pyarrow().to_string(),
                "history": []
            }
            
            # Intentar obtener historial (si está disponible)
            try:
                history = dt.history()
                info["history"] = history[:5]  # Últimas 5 versiones
            except:
                pass
            
            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    def list_tables(self) -> List[str]:
        """Lista todas las tablas Delta disponibles"""
        try:
            if not os.path.exists(self.base_path):
                return []
            
            tables = []
            for item in os.listdir(self.base_path):
                item_path = os.path.join(self.base_path, item)
                if os.path.isdir(item_path):
                    # Verificar si es una tabla Delta (tiene _delta_log)
                    if os.path.exists(os.path.join(item_path, "_delta_log")):
                        tables.append(item)
            
            return tables
            
        except Exception as e:
            self.logger.error(f"Error al listar tablas: {str(e)}")
            return []
    
    def get_table_stats(self, table_name: str) -> Dict:
        """Obtiene estadísticas de una tabla"""
        try:
            df = self.read_delta_table(table_name)
            if df is None:
                return {"error": "No se pudo leer la tabla"}
            
            stats = {
                "records": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
                "null_counts": df.isnull().sum().to_dict()
            }
            
            return stats
            
        except Exception as e:
            return {"error": str(e)}


def main():
    """Función de prueba"""
    manager = DeltaLakeManager()
    
    # Listar tablas disponibles
    tables = manager.list_tables()
    print(f"\nTablas Delta Lake disponibles: {tables}")
    
    # Información de cada tabla
    for table in tables:
        print(f"\n{'=' * 60}")
        print(f"Tabla: {table}")
        print(f"{'=' * 60}")
        
        info = manager.get_table_info(table)
        if "error" not in info:
            print(f"Versión: {info['version']}")
            print(f"Archivos: {len(info['files'])}")
            
            stats = manager.get_table_stats(table)
            if "error" not in stats:
                print(f"Registros: {stats['records']}")
                print(f"Columnas: {stats['columns']}")
                print(f"Memoria: {stats['memory_usage_mb']:.2f} MB")


if __name__ == "__main__":
    main()
