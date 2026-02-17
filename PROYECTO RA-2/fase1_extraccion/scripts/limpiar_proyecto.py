"""
Script de Limpieza Automática del Proyecto
Elimina archivos duplicados, obsoletos y antiguos para mantener el proyecto limpio

IMPORTANTE: Lee ANALISIS_LIMPIEZA.md antes de ejecutar este script
"""
import os
from pathlib import Path
from datetime import datetime


class ProyectoLimpieza:
    """Limpieza automática de archivos obsoletos del proyecto"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.archivos_eliminados = []
        self.errores = []
        
    def print_header(self, text):
        """Imprime un encabezado formateado"""
        print("\n" + "=" * 70)
        print(text.center(70))
        print("=" * 70)
    
    def eliminar_archivo(self, ruta_relativa, razon=""):
        """Elimina un archivo y registra la acción"""
        archivo = self.base_path / ruta_relativa
        
        if not archivo.exists():
            print(f"  ⊘ No existe: {ruta_relativa}")
            return False
        
        try:
            if archivo.is_file():
                archivo.unlink()
                self.archivos_eliminados.append((ruta_relativa, razon))
                print(f"  ✓ Eliminado: {ruta_relativa}")
                if razon:
                    print(f"    Razón: {razon}")
                return True
            else:
                print(f"  ⚠ Es un directorio (no se elimina): {ruta_relativa}")
                return False
                
        except Exception as e:
            error_msg = f"Error al eliminar {ruta_relativa}: {str(e)}"
            self.errores.append(error_msg)
            print(f"  ✗ {error_msg}")
            return False
    
    def limpiar_scripts_obsoletos(self):
        """Elimina scripts Python duplicados u obsoletos"""
        self.print_header("PASO 1: LIMPIANDO SCRIPTS PYTHON OBSOLETOS")
        
        scripts_obsoletos = [
            ("extraer_tags_series.py", "Duplicado - reemplazado por extraer_completo.py"),
            ("reconstruir_tags_series.py", "Funcionalidad ahora en el notebook"),
            ("verificar_tags_series.py", "Funcionalidad ahora en el notebook"),
            ("escaneo_completo.py", "Método obsoleto - extraer_completo.py es más eficiente"),
        ]
        
        print("\nEliminando scripts Python obsoletos...")
        for archivo, razon in scripts_obsoletos:
            self.eliminar_archivo(archivo, razon)
    
    def limpiar_scripts_batch(self):
        """Elimina scripts batch duplicados"""
        self.print_header("PASO 2: LIMPIANDO SCRIPTS BATCH DUPLICADOS")
        
        print("\nEliminando scripts batch redundantes...")
        self.eliminar_archivo("extraer_completo.bat", "Redundante - run.bat es más completo")
    
    def limpiar_logs_antiguos(self):
        """Elimina logs antiguos (más de 5 días)"""
        self.print_header("PASO 3: LIMPIANDO LOGS ANTIGUOS")
        
        logs_dir = self.base_path / "logs"
        
        if not logs_dir.exists():
            print("  ⊘ Directorio logs no existe")
            return
        
        print("\nBuscando logs antiguos (más de 5 días)...")
        
        # Logs específicos antiguos
        logs_antiguos = [
            "logs/delta_lake_20260210.log",
            "logs/delta_lake_20260211.log",
            "logs/events_extractor_20260210.log",
            "logs/events_extractor_20260211.log",
            "logs/markets_extractor_20260210.log",
            "logs/markets_extractor_20260211.log",
            "logs/series_extractor_20260210.log",
            "logs/series_extractor_20260211.log",
            "logs/tags_extractor_20260210.log",
            "logs/tags_extractor_20260211.log",
            "logs/main_extraction_20260210_173155.log",
            "logs/main_extraction_20260210_174408.log",
            "logs/main_extraction_20260210_174610.log",
            "logs/main_extraction_20260210_175132.log",
        ]
        
        for log_path in logs_antiguos:
            self.eliminar_archivo(log_path, "Log antiguo (más de 5 días)")
    
    def limpiar_csv_exportados(self, confirmar=True):
        """
        Elimina archivos CSV exportados (los datos están en Delta Lake)
        
        Args:
            confirmar: Si True, pide confirmación antes de eliminar
        """
        self.print_header("PASO 4: LIMPIANDO CSV EXPORTADOS (OPCIONAL)")
        
        csv_dir = self.base_path / "data" / "exported"
        
        if not csv_dir.exists():
            print("  ⊘ Directorio data/exported no existe")
            return
        
        csvs_exportados = list(csv_dir.glob("*.csv"))
        
        if not csvs_exportados:
            print("  ⊘ No hay archivos CSV para eliminar")
            return
        
        print(f"\nSe encontraron {len(csvs_exportados)} archivos CSV exportados:")
        for csv in csvs_exportados:
            print(f"  • {csv.name}")
        
        if confirmar:
            print("\n⚠️  ADVERTENCIA: Los datos están en Delta Lake, estos CSV son redundantes")
            print("   Se pueden regenerar desde el notebook (celda 10.1)")
            respuesta = input("\n¿Deseas eliminar estos archivos CSV? (s/N): ").strip().lower()
            
            if respuesta != 's':
                print("  ⊘ CSV exportados NO eliminados (conservados)")
                return
        
        print("\nEliminando archivos CSV exportados...")
        for csv in csvs_exportados:
            self.eliminar_archivo(f"data/exported/{csv.name}", "Redundante - datos en Delta Lake")
    
    def generar_reporte(self):
        """Genera un reporte de la limpieza realizada"""
        self.print_header("RESUMEN DE LIMPIEZA")
        
        print(f"\n✓ Archivos eliminados: {len(self.archivos_eliminados)}")
        print(f"✗ Errores encontrados: {len(self.errores)}")
        
        if self.archivos_eliminados:
            print("\n📋 ARCHIVOS ELIMINADOS:\n")
            for archivo, razon in self.archivos_eliminados:
                print(f"  ✓ {archivo}")
                if razon:
                    print(f"    → {razon}")
        
        if self.errores:
            print("\n⚠️  ERRORES:\n")
            for error in self.errores:
                print(f"  ✗ {error}")
        
        # Guardar reporte en archivo
        reporte_path = self.base_path / f"REPORTE_LIMPIEZA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(reporte_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("REPORTE DE LIMPIEZA DEL PROYECTO\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Archivos eliminados: {len(self.archivos_eliminados)}\n")
            f.write(f"Errores: {len(self.errores)}\n\n")
            
            if self.archivos_eliminados:
                f.write("ARCHIVOS ELIMINADOS:\n")
                f.write("-" * 70 + "\n")
                for archivo, razon in self.archivos_eliminados:
                    f.write(f"✓ {archivo}\n")
                    if razon:
                        f.write(f"  Razón: {razon}\n")
                f.write("\n")
            
            if self.errores:
                f.write("ERRORES:\n")
                f.write("-" * 70 + "\n")
                for error in self.errores:
                    f.write(f"✗ {error}\n")
        
        print(f"\n📄 Reporte guardado en: {reporte_path.name}")
    
    def ejecutar_limpieza_completa(self, eliminar_csvs=False):
        """Ejecuta la limpieza completa del proyecto"""
        print("\n")
        print("╔" + "═" * 68 + "╗")
        print("║" + " LIMPIEZA AUTOMÁTICA DEL PROYECTO ".center(68) + "║")
        print("╚" + "═" * 68 + "╝")
        print("\n⚠️  Este script eliminará archivos duplicados y obsoletos")
        print("   Revisa ANALISIS_LIMPIEZA.md para más detalles\n")
        
        # Paso 1: Scripts Python obsoletos
        self.limpiar_scripts_obsoletos()
        
        # Paso 2: Scripts batch duplicados
        self.limpiar_scripts_batch()
        
        # Paso 3: Logs antiguos
        self.limpiar_logs_antiguos()
        
        # Paso 4: CSV exportados (opcional)
        if eliminar_csvs:
            self.limpiar_csv_exportados(confirmar=True)
        
        # Generar reporte
        self.generar_reporte()
        
        print("\n" + "=" * 70)
        print("✅ LIMPIEZA COMPLETADA")
        print("=" * 70)


def main():
    """Función principal"""
    limpieza = ProyectoLimpieza()
    
    # Ejecutar limpieza completa
    # eliminar_csvs=False por defecto (no elimina CSVs automáticamente)
    limpieza.ejecutar_limpieza_completa(eliminar_csvs=False)
    
    print("\n💡 TIP: Para eliminar también los CSV exportados, ejecuta:")
    print("   limpieza = ProyectoLimpieza()")
    print("   limpieza.limpiar_csv_exportados(confirmar=True)")


if __name__ == "__main__":
    main()
