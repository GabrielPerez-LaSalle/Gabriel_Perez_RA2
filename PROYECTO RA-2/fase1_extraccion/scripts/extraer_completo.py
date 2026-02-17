"""
Script para extraer TODOS los datos de la API de Polymarket sin límites
Este script utiliza paginación automática para obtener todos los registros disponibles
"""
import sys
from datetime import datetime
from extract_tags import TagsExtractor
from extract_events import EventsExtractor
from extract_series import SeriesExtractor
from extract_markets import MarketsExtractor
from config import EXTRACTION_CONFIG


def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70)


def print_success(text):
    """Imprime un mensaje de éxito"""
    print(f"✓ {text}")


def print_error(text):
    """Imprime un mensaje de error"""
    print(f"✗ {text}")


def extract_all_data():
    """Extrae todos los datos de todos los endpoints"""
    
    print("\n╔" + "═" * 68 + "╗")
    print("║" + " EXTRACCIÓN COMPLETA DE DATOS - POLYMARKET API ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    
    print(f"\nConfiguración:")
    print(f"  - Límite por petición: {EXTRACTION_CONFIG['limit']}")
    print(f"  - Máximo de registros: {EXTRACTION_CONFIG['max_records']} (0 = SIN LÍMITE)")
    
    start_time = datetime.now()
    resultados = {}
    
    # 1. TAGS
    print_header("EXTRAYENDO TAGS")
    try:
        extractor_tags = TagsExtractor()
        all_tags = extractor_tags.extract_all_tags(max_records=0)
        if all_tags:
            extractor_tags.save_to_delta(all_tags, "tags")
            resultados['tags'] = len(all_tags)
            print_success(f"Tags extraídos y guardados: {len(all_tags):,} registros")
        else:
            print_error("No se pudieron extraer los tags")
            resultados['tags'] = 0
    except Exception as e:
        print_error(f"Error al extraer tags: {str(e)}")
        resultados['tags'] = 0
    
    # 2. EVENTS
    print_header("EXTRAYENDO EVENTS")
    try:
        extractor_events = EventsExtractor()
        all_events = extractor_events.extract_all_events(max_records=0)
        if all_events:
            extractor_events.save_to_delta(all_events, "events")
            resultados['events'] = len(all_events)
            print_success(f"Events extraídos y guardados: {len(all_events):,} registros")
        else:
            print_error("No se pudieron extraer los events")
            resultados['events'] = 0
    except Exception as e:
        print_error(f"Error al extraer events: {str(e)}")
        resultados['events'] = 0
    
    # 3. MARKETS
    print_header("EXTRAYENDO MARKETS")
    try:
        extractor_markets = MarketsExtractor()
        all_markets = extractor_markets.extract_all_markets(max_records=0)
        if all_markets:
            extractor_markets.save_to_delta(all_markets, "markets")
            resultados['markets'] = len(all_markets)
            print_success(f"Markets extraídos y guardados: {len(all_markets):,} registros")
        else:
            print_error("No se pudieron extraer los markets")
            resultados['markets'] = 0
    except Exception as e:
        print_error(f"Error al extraer markets: {str(e)}")
        resultados['markets'] = 0
    
    # 4. SERIES
    print_header("EXTRAYENDO SERIES")
    try:
        extractor_series = SeriesExtractor()
        all_series = extractor_series.extract_all_series(max_records=0)
        if all_series:
            extractor_series.save_to_delta(all_series, "series")
            resultados['series'] = len(all_series)
            print_success(f"Series extraídas y guardadas: {len(all_series):,} registros")
        else:
            print_error("No se pudieron extraer las series")
            resultados['series'] = 0
    except Exception as e:
        print_error(f"Error al extraer series: {str(e)}")
        resultados['series'] = 0
    
    # RESUMEN FINAL
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n\n╔" + "═" * 68 + "╗")
    print("║" + " RESUMEN DE EXTRACCIÓN COMPLETA ".center(68) + "║")
    print("╠" + "═" * 68 + "╣")
    print(f"║  Tags:    {resultados.get('tags', 0):>8,} registros extraídos" + " " * 33 + "║")
    print(f"║  Events:  {resultados.get('events', 0):>8,} registros extraídos" + " " * 33 + "║")
    print(f"║  Markets: {resultados.get('markets', 0):>8,} registros extraídos" + " " * 33 + "║")
    print(f"║  Series:  {resultados.get('series', 0):>8,} registros extraídos" + " " * 33 + "║")
    print("╠" + "═" * 68 + "╣")
    total = sum(resultados.values())
    print(f"║  TOTAL:   {total:>8,} registros extraídos" + " " * 33 + "║")
    print("╠" + "═" * 68 + "╣")
    print(f"║  Tiempo transcurrido: {str(duration).split('.')[0]}" + " " * (68 - 26 - len(str(duration).split('.')[0])) + "║")
    print("╚" + "═" * 68 + "╝")
    
    print(f"\n✓ Extracción completa finalizada")
    print(f"✓ Todos los datos han sido guardados en Delta Lake")
    print(f"✓ Puedes analizar los datos usando el notebook 'extraer_datos_delta_lake.ipynb'")
    
    return resultados


if __name__ == "__main__":
    print("\n" + "⚠" * 35)
    print("ADVERTENCIA: Este script extraerá TODOS los datos disponibles")
    print("de la API de Polymarket sin límites. Puede tardar varios minutos.")
    print("⚠" * 35)
    
    respuesta = input("\n¿Deseas continuar? (s/n): ").lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        try:
            resultados = extract_all_data()
            sys.exit(0)
        except KeyboardInterrupt:
            print("\n\n\n⚠ Extracción interrumpida por el usuario")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n✗ Error durante la extracción: {str(e)}")
            sys.exit(1)
    else:
        print("\nExtracción cancelada por el usuario.")
        sys.exit(0)
