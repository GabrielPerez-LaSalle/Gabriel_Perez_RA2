"""
Generador de Reporte de Volumetría en CSV
Genera un reporte completo con:
1. Cantidad de registros por entidad
2. Distribución de mercados (activos vs. cerrados)
3. Análisis de relaciones (mercados por evento/serie)
"""
import psycopg2
import csv
import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(__file__))
from fase2_warehouse.neondb_config import get_connection_string, DEFAULT_ENVIRONMENT


def generar_reporte_volumetria(environment=DEFAULT_ENVIRONMENT):
    """Genera los CSVs del reporte de volumetría"""
    
    print("="*70)
    print("GENERADOR DE REPORTE DE VOLUMETRÍA")
    print("="*70)
    print(f"\nEntorno: {environment}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Conectar
        conn = psycopg2.connect(get_connection_string(environment))
        cursor = conn.cursor()
        
        # Crear directorio de reportes
        reportes_dir = Path(__file__).parent / "reportes"
        reportes_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # ================================================================
        # 1. CANTIDAD DE REGISTROS POR ENTIDAD
        # ================================================================
        print("📊 [1/3] Generando: Cantidad de registros por entidad...")
        
        cursor.execute("""
            SELECT 'dim_time' as entidad, 'Dimensión Tiempo' as descripcion, COUNT(*) as total_registros 
            FROM dim_time
            UNION ALL
            SELECT 'dim_series', 'Dimensión Series', COUNT(*) FROM dim_series WHERE is_current = TRUE
            UNION ALL
            SELECT 'dim_tag', 'Dimensión Tags', COUNT(*) FROM dim_tag WHERE is_current = TRUE
            UNION ALL
            SELECT 'dim_event', 'Dimensión Eventos', COUNT(*) FROM dim_event WHERE is_current = TRUE
            UNION ALL
            SELECT 'dim_market', 'Dimensión Mercados', COUNT(*) FROM dim_market WHERE is_current = TRUE
            UNION ALL
            SELECT 'bridge_market_tag', 'Puente Market-Tag', COUNT(*) FROM bridge_market_tag
            UNION ALL
            SELECT 'fact_market_metrics', 'Tabla de Hechos (Métricas)', COUNT(*) FROM fact_market_metrics
            ORDER BY entidad;
        """)
        
        registros_entidad = cursor.fetchall()
        
        # Calcular total
        total_registros = sum(row[2] for row in registros_entidad)
        
        # Guardar CSV
        csv_path_1 = reportes_dir / f"volumetria_registros_por_entidad_{timestamp}.csv"
        with open(csv_path_1, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Entidad', 'Descripción', 'Total Registros', 'Porcentaje'])
            for row in registros_entidad:
                porcentaje = (row[2] / total_registros * 100) if total_registros > 0 else 0
                writer.writerow([row[0], row[1], row[2], f"{porcentaje:.2f}%"])
            writer.writerow(['TOTAL', 'Suma de todas las entidades', total_registros, '100.00%'])
        
        print(f"   ✓ Guardado: {csv_path_1.name}")
        
        # ================================================================
        # 2. DISTRIBUCIÓN DE MERCADOS (ACTIVOS VS CERRADOS)
        # ================================================================
        print("📊 [2/3] Generando: Distribución de mercados (activos vs. cerrados)...")
        
        # 2a. Resumen general
        cursor.execute("""
            SELECT 
                COUNT(*) as total_mercados,
                COUNT(CASE WHEN active = TRUE THEN 1 END) as mercados_activos,
                COUNT(CASE WHEN closed = TRUE THEN 1 END) as mercados_cerrados,
                COUNT(CASE WHEN active = FALSE AND closed = FALSE THEN 1 END) as otros
            FROM dim_market
            WHERE is_current = TRUE
        """)
        
        resumen = cursor.fetchone()
        
        csv_path_2a = reportes_dir / f"volumetria_distribucion_mercados_resumen_{timestamp}.csv"
        with open(csv_path_2a, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Estado', 'Cantidad', 'Porcentaje'])
            writer.writerow(['Total Mercados', resumen[0], '100.00%'])
            writer.writerow(['Activos', resumen[1], f"{(resumen[1]/resumen[0]*100):.2f}%"])
            writer.writerow(['Cerrados', resumen[2], f"{(resumen[2]/resumen[0]*100):.2f}%"])
            writer.writerow(['Otros', resumen[3], f"{(resumen[3]/resumen[0]*100):.2f}%"])
        
        print(f"   ✓ Guardado: {csv_path_2a.name}")
        
        # 2b. Por categoría
        cursor.execute("""
            SELECT 
                COALESCE(category, 'Sin categoría') as categoria,
                COUNT(*) as total_mercados,
                COUNT(CASE WHEN active = TRUE THEN 1 END) as activos,
                COUNT(CASE WHEN closed = TRUE THEN 1 END) as cerrados
            FROM dim_market
            WHERE is_current = TRUE
            GROUP BY category
            ORDER BY COUNT(*) DESC
        """)
        
        distribucion_categoria = cursor.fetchall()
        
        csv_path_2b = reportes_dir / f"volumetria_distribucion_mercados_por_categoria_{timestamp}.csv"
        with open(csv_path_2b, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Categoría', 'Total Mercados', 'Activos', 'Cerrados', '% Activos'])
            for row in distribucion_categoria:
                pct_activos = (row[2] / row[1] * 100) if row[1] > 0 else 0
                writer.writerow([row[0], row[1], row[2], row[3], f"{pct_activos:.2f}%"])
        
        print(f"   ✓ Guardado: {csv_path_2b.name}")
        
        # ================================================================
        # 3. ANÁLISIS DE RELACIONES
        # ================================================================
        print("📊 [3/3] Generando: Análisis de relaciones...")
        
        # 3a. Mercados por evento (top 50)
        cursor.execute("""
            SELECT 
                e.event_id,
                e.title as evento_titulo,
                e.category as categoria,
                COUNT(DISTINCT f.market_key) as num_mercados,
                COALESCE(SUM(f.volume), 0) as volumen_total,
                COALESCE(SUM(f.liquidity), 0) as liquidez_total
            FROM dim_event e
            LEFT JOIN fact_market_metrics f ON e.event_key = f.event_key
            WHERE e.is_current = TRUE
            GROUP BY e.event_key, e.event_id, e.title, e.category
            HAVING COUNT(DISTINCT f.market_key) > 0
            ORDER BY COUNT(DISTINCT f.market_key) DESC, COALESCE(SUM(f.volume), 0) DESC
            LIMIT 50
        """)
        
        mercados_por_evento = cursor.fetchall()
        
        csv_path_3a = reportes_dir / f"volumetria_mercados_por_evento_top50_{timestamp}.csv"
        with open(csv_path_3a, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Event ID', 'Evento', 'Categoría', 'Num Mercados', 'Volumen Total', 'Liquidez Total'])
            for row in mercados_por_evento:
                writer.writerow([row[0], row[1], row[2], row[3], f"{row[4]:.2f}", f"{row[5]:.2f}"])
        
        print(f"   ✓ Guardado: {csv_path_3a.name}")
        
        # 3b. Mercados por serie (top 30)
        cursor.execute("""
            SELECT 
                s.series_id,
                s.title as serie_titulo,
                COUNT(DISTINCT e.event_key) as num_eventos,
                COUNT(DISTINCT f.market_key) as num_mercados,
                COALESCE(SUM(f.volume), 0) as volumen_total
            FROM dim_series s
            LEFT JOIN dim_event e ON s.slug = e.series_slug
            LEFT JOIN fact_market_metrics f ON e.event_key = f.event_key
            WHERE s.is_current = TRUE
            GROUP BY s.series_key, s.series_id, s.title
            HAVING COUNT(DISTINCT f.market_key) > 0
            ORDER BY COUNT(DISTINCT f.market_key) DESC
            LIMIT 30
        """)
        
        mercados_por_serie = cursor.fetchall()
        
        csv_path_3b = reportes_dir / f"volumetria_mercados_por_serie_top30_{timestamp}.csv"
        with open(csv_path_3b, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Series ID', 'Serie', 'Num Eventos', 'Num Mercados', 'Volumen Total'])
            for row in mercados_por_serie:
                writer.writerow([row[0], row[1], row[2], row[3], f"{row[4]:.2f}"])
        
        print(f"   ✓ Guardado: {csv_path_3b.name}")
        
        # 3c. Mercados por tag (top 30)
        cursor.execute("""
            SELECT 
                t.tag_id,
                t.label as tag_nombre,
                t.level as nivel_jerarquico,
                COUNT(DISTINCT bmt.market_key) as num_mercados
            FROM dim_tag t
            LEFT JOIN bridge_market_tag bmt ON t.tag_key = bmt.tag_key
            WHERE t.is_current = TRUE
            GROUP BY t.tag_key, t.tag_id, t.label, t.level
            HAVING COUNT(DISTINCT bmt.market_key) > 0
            ORDER BY COUNT(DISTINCT bmt.market_key) DESC
            LIMIT 30
        """)
        
        mercados_por_tag = cursor.fetchall()
        
        csv_path_3c = reportes_dir / f"volumetria_mercados_por_tag_top30_{timestamp}.csv"
        with open(csv_path_3c, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Tag ID', 'Tag', 'Nivel Jerárquico', 'Num Mercados'])
            for row in mercados_por_tag:
                writer.writerow([row[0], row[1], row[2], row[3]])
        
        print(f"   ✓ Guardado: {csv_path_3c.name}")
        
        # 3d. Resumen de relaciones
        cursor.execute("""
            SELECT 
                'Series' as entidad,
                COUNT(*) as total
            FROM dim_series
            WHERE is_current = TRUE
            
            UNION ALL
            
            SELECT 
                'Eventos',
                COUNT(*)
            FROM dim_event
            WHERE is_current = TRUE
            
            UNION ALL
            
            SELECT 
                'Mercados',
                COUNT(*)
            FROM dim_market
            WHERE is_current = TRUE
            
            UNION ALL
            
            SELECT 
                'Tags',
                COUNT(*)
            FROM dim_tag
            WHERE is_current = TRUE
            
            UNION ALL
            
            SELECT 
                'Relaciones Market-Tag',
                COUNT(*)
            FROM bridge_market_tag
        """)
        
        resumen_relaciones = cursor.fetchall()
        
        # Calcular promedios
        cursor.execute("""
            SELECT 
                'Promedio mercados por evento' as metrica,
                ROUND(AVG(num_markets), 2) as valor
            FROM (
                SELECT event_key, COUNT(DISTINCT market_key) as num_markets
                FROM fact_market_metrics
                GROUP BY event_key
            ) subq
            
            UNION ALL
            
            SELECT 
                'Promedio tags por mercado',
                ROUND(AVG(num_tags), 2)
            FROM (
                SELECT market_key, COUNT(DISTINCT tag_key) as num_tags
                FROM bridge_market_tag
                GROUP BY market_key
            ) subq
        """)
        
        promedios = cursor.fetchall()
        
        csv_path_3d = reportes_dir / f"volumetria_resumen_relaciones_{timestamp}.csv"
        with open(csv_path_3d, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Métrica', 'Valor'])
            for row in resumen_relaciones:
                writer.writerow(row)
            writer.writerow([])  # Línea vacía
            writer.writerow(['Promedios', ''])
            for row in promedios:
                writer.writerow(row)
        
        print(f"   ✓ Guardado: {csv_path_3d.name}")
        
        # ================================================================
        # 4. GENERAR ÍNDICE
        # ================================================================
        print("\n📄 Generando índice de archivos...")
        
        csv_path_indice = reportes_dir / f"INDICE_REPORTE_VOLUMETRIA_{timestamp}.txt"
        with open(csv_path_indice, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("ÍNDICE DEL REPORTE DE VOLUMETRÍA\n")
            f.write("="*70 + "\n\n")
            f.write(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Entorno: {environment}\n\n")
            
            f.write("ARCHIVOS GENERADOS:\n")
            f.write("-"*70 + "\n\n")
            
            f.write("1. CANTIDAD DE REGISTROS POR ENTIDAD\n")
            f.write(f"   {csv_path_1.name}\n")
            f.write(f"   Total registros: {total_registros:,}\n\n")
            
            f.write("2. DISTRIBUCIÓN DE MERCADOS (ACTIVOS VS. CERRADOS)\n")
            f.write(f"   {csv_path_2a.name}\n")
            f.write(f"   {csv_path_2b.name}\n")
            f.write(f"   Total mercados: {resumen[0]:,}\n")
            f.write(f"   Activos: {resumen[1]:,} ({(resumen[1]/resumen[0]*100):.2f}%)\n")
            f.write(f"   Cerrados: {resumen[2]:,} ({(resumen[2]/resumen[0]*100):.2f}%)\n\n")
            
            f.write("3. ANÁLISIS DE RELACIONES\n")
            f.write(f"   {csv_path_3a.name} (Top 50 eventos)\n")
            f.write(f"   {csv_path_3b.name} (Top 30 series)\n")
            f.write(f"   {csv_path_3c.name} (Top 30 tags)\n")
            f.write(f"   {csv_path_3d.name} (Resumen)\n\n")
            
            f.write("="*70 + "\n")
            f.write("Todos los archivos están en la carpeta: reportes/\n")
            f.write("="*70 + "\n")
        
        print(f"   ✓ Guardado: {csv_path_indice.name}")
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        # ================================================================
        # RESUMEN FINAL
        # ================================================================
        print("\n" + "="*70)
        print("✅ REPORTE DE VOLUMETRÍA GENERADO EXITOSAMENTE")
        print("="*70)
        print(f"\n📁 Ubicación: {reportes_dir.absolute()}\n")
        print("Archivos generados:")
        print(f"  1. {csv_path_1.name}")
        print(f"  2. {csv_path_2a.name}")
        print(f"  3. {csv_path_2b.name}")
        print(f"  4. {csv_path_3a.name}")
        print(f"  5. {csv_path_3b.name}")
        print(f"  6. {csv_path_3c.name}")
        print(f"  7. {csv_path_3d.name}")
        print(f"  8. {csv_path_indice.name} (índice)")
        print("\n" + "="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    environment = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ENVIRONMENT
    
    if environment not in ['development', 'production']:
        print("❌ Ambiente inválido. Use 'development' o 'production'")
        sys.exit(1)
    
    success = generar_reporte_volumetria(environment)
    sys.exit(0 if success else 1)
