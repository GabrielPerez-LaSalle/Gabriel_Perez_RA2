"""
Módulo para extraer datos de Series desde la API de Polymarket
"""
import requests
import json
import logging
import time
import warnings
from datetime import datetime
from typing import List, Dict, Optional
from config import ENDPOINTS, EXTRACTION_CONFIG, REQUEST_TIMEOUT, HEADERS, DATA_DIR, JSON_CONFIG, VERIFY_SSL, RETRY_CONFIG
from delta_utils import DeltaLakeManager

# Suprimir warnings de SSL
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class SeriesExtractor:
    """Clase para extraer datos de Series"""
    
    def __init__(self):
        self.endpoint = ENDPOINTS["series"]
        self.logger = self._setup_logger()
        self.delta_manager = DeltaLakeManager()
        
    def _setup_logger(self) -> logging.Logger:
        """Configurar el logger para el extractor"""
        logger = logging.getLogger("SeriesExtractor")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler(f"logs/series_extractor_{datetime.now().strftime('%Y%m%d')}.log")
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def extract_series(self, limit: int = None, offset: int = 0, **kwargs) -> Optional[List[Dict]]:
        """
        Extrae series desde la API de Polymarket
        
        Args:
            limit: Límite de registros por petición
            offset: Offset para paginación
            **kwargs: Parámetros adicionales de filtrado
            
        Returns:
            Lista de diccionarios con los datos de series o None si hay error
        """
        if limit is None:
            limit = EXTRACTION_CONFIG["limit"]
            
        params = {
            "limit": limit,
            "offset": offset,
            **kwargs
        }
        
        for attempt in range(RETRY_CONFIG['max_retries']):
            try:
                self.logger.info(f"Extrayendo series - Limit: {limit}, Offset: {offset} (Intento {attempt + 1}/{RETRY_CONFIG['max_retries']})")
                response = requests.get(
                    self.endpoint,
                    params=params,
                    headers=HEADERS,
                    timeout=REQUEST_TIMEOUT,
                    verify=VERIFY_SSL
                )
                response.raise_for_status()
                
                data = response.json()
                self.logger.info(f"Series extraídas exitosamente: {len(data)} registros")
                return data
                
            except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
                self.logger.warning(f"Error de conexión/SSL en intento {attempt + 1}: {str(e)[:100]}")
                if attempt < RETRY_CONFIG['max_retries'] - 1:
                    delay = RETRY_CONFIG['retry_delay'] * (RETRY_CONFIG['backoff_factor'] ** attempt)
                    self.logger.info(f"Reintentando en {delay:.1f} segundos...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"Error después de {RETRY_CONFIG['max_retries']} intentos")
                    return None
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error al extraer series: {str(e)}")
                return None
        
        return None
    
    def extract_all_series(self, max_records: int = None) -> List[Dict]:
        """
        Extrae todas las series disponibles usando paginación
        
        Args:
            max_records: Número máximo de registros a extraer (None = todos)
            
        Returns:
            Lista completa de series
        """
        all_series = []
        offset = 0
        limit = 300  # API máximo = 300 por petición
        
        if max_records is None:
            max_records = EXTRACTION_CONFIG["max_records"]
        
        self.logger.info("Iniciando extracción completa de series")
        self.logger.info(f"Usando límite de {limit} registros por petición")
        
        while True:
            series = self.extract_series(limit=limit, offset=offset)
            
            # Si no hay datos o está vacío, terminar
            if not series or len(series) == 0:
                self.logger.info("No hay más datos disponibles")
                break
            
            # Agregar las nuevas series
            all_series.extend(series)
            self.logger.info(f"Petición offset={offset}: {len(series)} registros | Total acumulado: {len(all_series)}")
            
            # Verificar si alcanzamos el límite máximo deseado
            if max_records > 0 and len(all_series) >= max_records:
                all_series = all_series[:max_records]
                self.logger.info(f"Alcanzado el límite máximo de {max_records} registros")
                break
            
            # Continuar solo si obtuvimos datos (aunque sea menos del límite)
            # La API puede devolver menos records si estamos cerca del final
            offset += len(series)
        
        self.logger.info(f"Extracción completa finalizada: {len(all_series)} series")
        return all_series
    
    def save_to_json(self, data: List[Dict], filename: str = None) -> bool:
        """
        Guarda los datos en un archivo JSON
        
        Args:
            data: Lista de datos a guardar
            filename: Nombre del archivo (opcional)
            
        Returns:
            True si se guardó exitosamente, False en caso contrario
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"series_{timestamp}.json"
        
        filepath = f"{DATA_DIR}/{filename}"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, **JSON_CONFIG)
            
            self.logger.info(f"Datos guardados exitosamente en {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al guardar datos: {str(e)}")
            return False
    
    def save_to_delta(self, data: List[Dict], table_name: str = "series") -> bool:
        """
        Guarda los datos en formato Delta Lake
        
        Args:
            data: Lista de datos a guardar
            table_name: Nombre de la tabla Delta (por defecto: series)
            
        Returns:
            True si se guardó exitosamente, False en caso contrario
        """
        try:
            success = self.delta_manager.save_to_delta(data, table_name)
            
            if success:
                self.logger.info(f"Datos guardados exitosamente en Delta Lake: {table_name}")
                return True
            else:
                self.logger.error(f"Error al guardar datos en Delta Lake: {table_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error al guardar en Delta Lake: {str(e)}")
            return False


def main():
    """Función principal para ejecutar la extracción"""
    extractor = SeriesExtractor()
    
    # Extraer todas las series
    series = extractor.extract_all_series()
    
    if series:
        print(f"\n✓ Se extrajeron {len(series)} series")
        
        # Guardar en JSON
        if extractor.save_to_json(series):
            print("✓ Datos guardados exitosamente")
        else:
            print("✗ Error al guardar los datos")
    else:
        print("✗ No se pudieron extraer las series")


if __name__ == "__main__":
    main()
