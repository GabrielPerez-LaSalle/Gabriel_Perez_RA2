"""
Script Principal - FASE 1: Extracción de Datos de Polymarket
Este script orquesta la extracción de datos de todos los endpoints de la API de Polymarket
"""
import logging
import sys
from datetime import datetime
from typing import Dict, List
from extract_tags import TagsExtractor
from extract_events import EventsExtractor
from extract_series import SeriesExtractor
from extract_markets import MarketsExtractor


class PolymarketDataExtractor:
    """Clase principal para orquestar la extracción de datos"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.results = {
            "tags": None,
            "events": None,
            "series": None,
            "markets": None
        }
        
    def _setup_logger(self) -> logging.Logger:
        """Configurar el logger principal"""
        logger = logging.getLogger("PolymarketDataExtractor")
        logger.setLevel(logging.INFO)
        
        # Handler para archivo
        file_handler = logging.FileHandler(
            f"logs/main_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def extract_tags(self) -> bool:
        """Extrae datos de Tags"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("Iniciando extracción de TAGS")
            self.logger.info("=" * 60)
            
            extractor = TagsExtractor()
            tags = extractor.extract_all_tags()
            
            if tags:
                self.results["tags"] = len(tags)
                extractor.save_to_delta(tags, "tags")
                self.logger.info(f"✓ Tags extraídos: {len(tags)} registros")
                return True
            else:
                self.logger.error("✗ No se pudieron extraer los tags")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Error en extracción de tags: {str(e)}")
            return False
    
    def extract_events(self) -> bool:
        """Extrae datos de Events"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("Iniciando extracción de EVENTS")
            self.logger.info("=" * 60)
            
            extractor = EventsExtractor()
            events = extractor.extract_all_events()
            
            if events:
                self.results["events"] = len(events)
                extractor.save_to_delta(events, "events")
                self.logger.info(f"✓ Events extraídos: {len(events)} registros")
                return True
            else:
                self.logger.error("✗ No se pudieron extraer los events")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Error en extracción de events: {str(e)}")
            return False
    
    def extract_series(self) -> bool:
        """Extrae datos de Series"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("Iniciando extracción de SERIES")
            self.logger.info("=" * 60)
            
            extractor = SeriesExtractor()
            series = extractor.extract_all_series()
            
            if series:
                self.results["series"] = len(series)
                extractor.save_to_delta(series, "series")
                self.logger.info(f"✓ Series extraídas: {len(series)} registros")
                return True
            else:
                self.logger.error("✗ No se pudieron extraer las series")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Error en extracción de series: {str(e)}")
            return False
    
    def extract_markets(self) -> bool:
        """Extrae datos de Markets"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("Iniciando extracción de MARKETS")
            self.logger.info("=" * 60)
            
            extractor = MarketsExtractor()
            markets = extractor.extract_all_markets()
            
            if markets:
                self.results["markets"] = len(markets)
                extractor.save_to_delta(markets, "markets")
                self.logger.info(f"✓ Markets extraídos: {len(markets)} registros")
                return True
            else:
                self.logger.error("✗ No se pudieron extraer los markets")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Error en extracción de markets: {str(e)}")
            return False
    
    def run_all_extractions(self) -> Dict[str, bool]:
        """Ejecuta todas las extracciones"""
        self.logger.info("╔" + "═" * 58 + "╗")
        self.logger.info("║" + " FASE 1: EXTRACCIÓN DE DATOS DE POLYMARKET ".center(58) + "║")
        self.logger.info("╚" + "═" * 58 + "╝")
        
        start_time = datetime.now()
        
        extraction_results = {
            "tags": self.extract_tags(),
            "events": self.extract_events(),
            "series": self.extract_series(),
            "markets": self.extract_markets()
        }
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Resumen de resultados
        self.logger.info("\n" + "=" * 60)
        self.logger.info("RESUMEN DE EXTRACCIÓN")
        self.logger.info("=" * 60)
        
        for endpoint, success in extraction_results.items():
            status = "✓ Exitoso" if success else "✗ Fallido"
            count = self.results.get(endpoint, 0) if success else 0
            self.logger.info(f"{endpoint.upper():15} - {status:12} - {count} registros")
        
        self.logger.info("=" * 60)
        self.logger.info(f"Tiempo total de ejecución: {duration}")
        self.logger.info("=" * 60)
        
        return extraction_results
    
    def print_summary(self):
        """Imprime un resumen visual de la extracción"""
        print("\n" + "╔" + "═" * 58 + "╗")
        print("║" + " RESUMEN FINAL DE EXTRACCIÓN ".center(58) + "║")
        print("╠" + "═" * 58 + "╣")
        
        for endpoint, count in self.results.items():
            if count is not None:
                print(f"║  {endpoint.upper():12} : {count:6} registros extraídos {' ' * 19}║")
            else:
                print(f"║  {endpoint.upper():12} : No se pudieron extraer datos {' ' * 10}║")
        
        print("╚" + "═" * 58 + "╝\n")


def main():
    """Función principal"""
    print("\n" + "=" * 60)
    print(" POLYMARKET DATA EXTRACTOR - FASE 1 ".center(60))
    print("=" * 60 + "\n")
    
    extractor = PolymarketDataExtractor()
    
    try:
        # Ejecutar todas las extracciones
        results = extractor.run_all_extractions()
        
        # Mostrar resumen
        extractor.print_summary()
        
        # Verificar si todas las extracciones fueron exitosas
        if all(results.values()):
            print("✓ Todas las extracciones se completaron exitosamente")
            return 0
        else:
            print("⚠ Algunas extracciones fallaron. Revisa los logs para más detalles.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠ Extracción interrumpida por el usuario")
        return 2
    except Exception as e:
        print(f"\n✗ Error crítico: {str(e)}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
