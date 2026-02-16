"""
Módulo para extraer datos de Markets desde la API de Polymarket
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


class MarketsExtractor:
    """Clase para extraer datos de Markets"""
    
    def __init__(self):
        self.endpoint = ENDPOINTS["markets"]
        self.logger = self._setup_logger()
        self.delta_manager = DeltaLakeManager()
        
    def _setup_logger(self) -> logging.Logger:
        """Configurar el logger para el extractor"""
        logger = logging.getLogger("MarketsExtractor")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler(f"logs/markets_extractor_{datetime.now().strftime('%Y%m%d')}.log")
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def extract_markets(self, limit: int = None, offset: int = 0, **kwargs) -> Optional[List[Dict]]:
        """
        Extrae markets desde la API de Polymarket
        
        Args:
            limit: Límite de registros por petición
            offset: Offset para paginación
            **kwargs: Parámetros adicionales de filtrado
            
        Returns:
            Lista de diccionarios con los datos de markets o None si hay error
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
                self.logger.info(f"Extrayendo markets - Limit: {limit}, Offset: {offset} (Intento {attempt + 1}/{RETRY_CONFIG['max_retries']})")
                response = requests.get(
                    self.endpoint,
                    params=params,
                    headers=HEADERS,
                    timeout=REQUEST_TIMEOUT,
                    verify=VERIFY_SSL
                )
                response.raise_for_status()
                
                data = response.json()
                self.logger.info(f"Markets extraídos exitosamente: {len(data)} registros")
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
                self.logger.error(f"Error al extraer markets: {str(e)}")
                return None
        
        return None
    
    def extract_all_markets(self, max_records: int = None) -> List[Dict]:
        """
        Extrae todos los markets disponibles usando paginación
        
        Args:
            max_records: Número máximo de registros a extraer (None = todos)
            
        Returns:
            Lista completa de markets
        """
        all_markets = []
        offset = 0
        limit = EXTRACTION_CONFIG["limit"]
        
        if max_records is None:
            max_records = EXTRACTION_CONFIG["max_records"]
        
        self.logger.info("Iniciando extracción completa de markets")
        
        while True:
            markets = self.extract_markets(limit=limit, offset=offset)
            
            if not markets or len(markets) == 0:
                break
                
            all_markets.extend(markets)
            self.logger.info(f"Total acumulado de markets: {len(all_markets)}")
            
            if max_records > 0 and len(all_markets) >= max_records:
                all_markets = all_markets[:max_records]
                break
                
            if len(markets) < limit:
                break
                
            offset += limit
        
        self.logger.info(f"Extracción completa finalizada: {len(all_markets)} markets")
        return all_markets
    
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
            filename = f"markets_{timestamp}.json"
        
        filepath = f"{DATA_DIR}/{filename}"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, **JSON_CONFIG)
            
            self.logger.info(f"Datos guardados exitosamente en {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al guardar datos: {str(e)}")
            return False
    
    def save_to_delta(self, data: List[Dict], table_name: str = "markets") -> bool:
        """
        Guarda los datos en formato Delta Lake
        
        Args:
            data: Lista de datos a guardar
            table_name: Nombre de la tabla Delta (por defecto: markets)
            
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
    extractor = MarketsExtractor()
    
    # Extraer todos los markets
    markets = extractor.extract_all_markets()
    
    if markets:
        print(f"\n✓ Se extrajeron {len(markets)} markets")
        
        # Guardar en JSON
        if extractor.save_to_json(markets):
            print("✓ Datos guardados exitosamente")
        else:
            print("✗ Error al guardar los datos")
    else:
        print("✗ No se pudieron extraer los markets")


if __name__ == "__main__":
    main()
