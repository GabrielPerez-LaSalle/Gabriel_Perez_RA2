"""
Script para extraer datos de Tags y Series con mayor volumen de registros
"""
from extract_tags import TagsExtractor
from extract_series import SeriesExtractor
from datetime import datetime


def main():
    print("=" * 80)
    print("EXTRACCIÓN DE TAGS Y SERIES - POLYMARKET API")
    print("=" * 80)
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # ========== EXTRACCIÓN DE TAGS ==========
    print("\n" + "=" * 80)
    print("EXTRAYENDO TAGS")
    print("=" * 80)
    
    tags_extractor = TagsExtractor()
    tags = tags_extractor.extract_all_tags()
    
    if tags:
        print(f"\n✓ TAGS EXTRAÍDOS: {len(tags)} registros")
        
        # Guardar en Delta Lake
        if tags_extractor.save_to_delta(tags):
            print("✓ Tags guardados exitosamente en Delta Lake")
        else:
            print("✗ Error al guardar tags en Delta Lake")
    else:
        print("\n✗ No se pudieron extraer los tags")
    
    # ========== EXTRACCIÓN DE SERIES ==========
    print("\n" + "=" * 80)
    print("EXTRAYENDO SERIES")
    print("=" * 80)
    
    series_extractor = SeriesExtractor()
    series = series_extractor.extract_all_series()
    
    if series:
        print(f"\n✓ SERIES EXTRAÍDAS: {len(series)} registros")
        
        # Guardar en Delta Lake
        if series_extractor.save_to_delta(series):
            print("✓ Series guardadas exitosamente en Delta Lake")
        else:
            print("✗ Error al guardar series en Delta Lake")
    else:
        print("\n✗ No se pudieron extraer las series")
    
    # ========== RESUMEN FINAL ==========
    print("\n" + "=" * 80)
    print("RESUMEN DE EXTRACCIÓN")
    print("=" * 80)
    print(f"Tags extraídos:   {len(tags) if tags else 0} registros")
    print(f"Series extraídas: {len(series) if series else 0} registros")
    print(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    main()
