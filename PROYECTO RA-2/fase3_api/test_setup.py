"""
Script de prueba para verificar la instalación y configuración de la API
"""
import sys
import os

def test_imports():
    """Verifica que se puedan importar los módulos necesarios"""
    print("🧪 Verificando imports...")
    try:
        import fastapi
        print(f"  ✅ FastAPI v{fastapi.__version__}")
    except ImportError:
        print("  ❌ FastAPI no instalado")
        return False
    
    try:
        import uvicorn
        print(f"  ✅ Uvicorn instalado")
    except ImportError:
        print("  ❌ Uvicorn no instalado")
        return False
    
    try:
        import pydantic
        print(f"  ✅ Pydantic v{pydantic.__version__}")
    except ImportError:
        print("  ❌ Pydantic no instalado")
        return False
    
    try:
        import psycopg2
        print(f"  ✅ psycopg2 instalado")
    except ImportError:
        print("  ❌ psycopg2 no instalado")
        return False
    
    try:
        from dotenv import load_dotenv
        print(f"  ✅ python-dotenv instalado")
    except ImportError:
        print("  ❌ python-dotenv no instalado")
        return False
    
    return True

def test_local_imports():
    """Verifica que se puedan importar los módulos locales"""
    print("\n🧪 Verificando módulos locales...")
    try:
        from config import settings
        print(f"  ✅ config.py - Settings cargado")
        print(f"     - API Title: {settings.API_TITLE}")
        print(f"     - API Version: {settings.API_VERSION}")
        print(f"     - DB Host: {settings.DB_HOST}")
    except Exception as e:
        print(f"  ❌ Error en config.py: {e}")
        return False
    
    try:
        from database import test_connection
        print(f"  ✅ database.py importado")
    except Exception as e:
        print(f"  ❌ Error en database.py: {e}")
        return False
    
    try:
        import models
        print(f"  ✅ models.py importado")
    except Exception as e:
        print(f"  ❌ Error en models.py: {e}")
        return False
    
    try:
        from routers import markets, events, series, tags, analytics
        print(f"  ✅ Todos los routers importados")
    except Exception as e:
        print(f"  ❌ Error en routers: {e}")
        return False
    
    return True

def test_database_connection():
    """Verifica la conexión a la base de datos"""
    print("\n🧪 Verificando conexión a base de datos...")
    try:
        from database import test_connection
        if test_connection():
            print("  ✅ Conexión a NeonDB exitosa")
            return True
        else:
            print("  ❌ No se pudo conectar a NeonDB")
            print("     Verifica las credenciales en .env")
            return False
    except Exception as e:
        print(f"  ❌ Error al probar conexión: {e}")
        return False

def test_env_file():
    """Verifica que exista el archivo .env"""
    print("\n🧪 Verificando archivo .env...")
    if os.path.exists('.env'):
        print("  ✅ Archivo .env encontrado")
        return True
    else:
        print("  ⚠️  Archivo .env no encontrado")
        print("     Copia .env.example a .env y completa las credenciales")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("=" * 60)
    print("  Polymarket Data Warehouse API - Test de Configuración")
    print("=" * 60)
    
    results = []
    
    # Prueba 1: Verificar archivo .env
    results.append(("Archivo .env", test_env_file()))
    
    # Prueba 2: Verificar imports externos
    results.append(("Dependencias externas", test_imports()))
    
    # Prueba 3: Verificar imports locales
    results.append(("Módulos locales", test_local_imports()))
    
    # Prueba 4: Verificar conexión a DB
    results.append(("Conexión a base de datos", test_database_connection()))
    
    # Resumen
    print("\n" + "=" * 60)
    print("  RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("=" * 60)
    print(f"Resultado: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n🎉 ¡Todo configurado correctamente!")
        print("   Ejecuta 'python main.py' para iniciar la API")
        return 0
    else:
        print("\n⚠️  Algunas pruebas fallaron")
        print("   Revisa los mensajes de error arriba")
        return 1

if __name__ == "__main__":
    sys.exit(main())
