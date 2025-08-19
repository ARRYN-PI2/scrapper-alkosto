#!/usr/bin/env python3
"""
prueba_4.py - Script de prueba para el scraper de Alkosto

PROPÓSITO:
Este script prueba la nueva funcionalidad del AlkostoScraper que permite
cargar TODOS los productos (155 en total) haciendo clic automáticamente 
en el botón "Mostrar más productos" usando Selenium.

FUNCIONALIDAD PROBADA:
- Carga dinámica de productos mediante clics en botón "Mostrar más"
- Extracción de URLs de todos los productos disponibles
- Manejo de esperas y timeouts para carga AJAX
- Detección automática cuando no hay más productos

PROBLEMA RESUELTO:
Antes solo podíamos obtener los primeros 25 productos porque Alkosto
usa carga dinámica en lugar de paginación por URL. Ahora el scraper
simula clics del usuario para cargar todos los productos.

EJECUCIÓN:
python prueba_4.py

SALIDA ESPERADA:
- Log detallado del proceso de carga
- Lista de URLs de productos encontrados
- Archivo JSON con todos los productos para verificación
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Agregar el directorio src al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.infraestructure.scrapers.alkosto_scraper import AlkostoScraper
    from loguru import logger
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("💡 Asegúrate de estar en la raíz del proyecto y que src/ existe")
    sys.exit(1)

def main():
    """
    Función principal que ejecuta la prueba del scraper de Alkosto.
    """
    print("="*60)
    print("🧪 PRUEBA 4: Scraper de Alkosto con carga dinámica")
    print("="*60)
    print()
    print("📋 OBJETIVO:")
    print("   Probar que el scraper puede cargar TODOS los productos (155)")
    print("   usando clics automáticos en 'Mostrar más productos'")
    print()
    print("⚠️  NOTA:")
    print("   Esta prueba abre un navegador Chrome y toma unos minutos")
    print("   Se recomienda ejecutar sin modo headless la primera vez")
    print()
    
    # Preguntar al usuario si quiere continuar
    response = input("¿Continuar con la prueba? (s/n): ").lower().strip()
    if response not in ['s', 'si', 'y', 'yes']:
        print("❌ Prueba cancelada por el usuario")
        return
    
    print("\n🚀 Iniciando prueba...")
    
    # Configurar logging más detallado
    logger.remove()  # Remover configuración por defecto
    logger.add(
        sys.stdout, 
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level="INFO"
    )
    
    # Crear instancia del scraper
    print("\n📦 Creando instancia del AlkostoScraper...")
    scraper = AlkostoScraper(delay_between_requests=1.0, max_retries=3)
    
    # Variables para medir el rendimiento
    start_time = datetime.now()
    
    try:
        print("\n🎯 Ejecutando get_product_urls() para obtener TODOS los productos...")
        print("   (Esto puede tomar 3-5 minutos dependiendo de la velocidad de internet)")
        
        # NOTA: Cambiar max_products para pruebas más rápidas
        # Para prueba completa: max_products=155
        # Para prueba rápida: max_products=50
        product_urls = scraper.get_product_urls_with_load_more(max_products=155)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "="*60)
        print("📊 RESULTADOS DE LA PRUEBA")
        print("="*60)
        print(f"✅ Productos encontrados: {len(product_urls)}")
        print(f"⏱️  Tiempo total: {duration}")
        print(f"⚡ Velocidad: {len(product_urls)/duration.total_seconds():.2f} productos/segundo")
        
        if len(product_urls) >= 100:
            print("🎉 ¡ÉXITO! Se cargaron más de 100 productos")
        elif len(product_urls) >= 50:
            print("✅ PARCIAL: Se cargaron más de 50 productos")
        else:
            print("⚠️  LIMITADO: Se cargaron menos de 50 productos")
        
        # Mostrar algunas URLs de ejemplo
        if product_urls:
            print(f"\n📋 Primeras 5 URLs encontradas:")
            for i, url in enumerate(product_urls[:5], 1):
                print(f"   {i}. {url}")
            
            if len(product_urls) > 5:
                print(f"   ... y {len(product_urls) - 5} más")
        
        # Guardar resultados en archivo JSON para verificación
        output_file = f"prueba_4_resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_productos": len(product_urls),
            "tiempo_ejecucion": str(duration),
            "productos_por_segundo": len(product_urls)/duration.total_seconds(),
            "urls": product_urls
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: {output_file}")
        
        # Prueba adicional: scraping de un producto
        if product_urls:
            print(f"\n🔍 PRUEBA ADICIONAL: Scraping de un producto individual...")
            try:
                sample_product = scraper.scrape_product(product_urls[0])
                print(f"✅ Producto scrapeado exitosamente:")
                print(f"   Nombre: {sample_product.nombre}")
                print(f"   Precio: ${sample_product.precio:,.0f}")
                print(f"   Marca: {sample_product.marca}")
                print(f"   Tamaño: {sample_product.tamano_pulgadas}\"")
                print(f"   Resolución: {sample_product.resolucion}")
            except Exception as e:
                print(f"❌ Error en scraping individual: {e}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Prueba interrumpida por el usuario")
        return
        
    except Exception as e:
        print(f"\n❌ ERROR durante la prueba: {e}")
        logger.exception("Detalles del error:")
        return
    
    print("\n🏁 Prueba completada!")
    print("\n💡 PRÓXIMOS PASOS:")
    print("   1. Si la prueba fue exitosa, puedes usar el scraper en producción")
    print("   2. Ajusta max_products según tus necesidades")
    print("   3. Considera agregar modo headless para ejecución automática")

def verificar_dependencias():
    """
    Verifica que todas las dependencias estén instaladas.
    """
    # Mapeo de nombres de paquetes pip a nombres de módulos Python
    dependencias = {
        'selenium': 'selenium',
        'beautifulsoup4': 'bs4',  # beautifulsoup4 se importa como bs4
        'loguru': 'loguru',
        'webdriver-manager': 'webdriver_manager'
    }
    
    faltantes = []
    for pip_name, module_name in dependencias.items():
        try:
            __import__(module_name)
        except ImportError:
            faltantes.append(pip_name)
    
    if faltantes:
        print("❌ Dependencias faltantes:")
        for dep in faltantes:
            print(f"   - {dep}")
        print(f"\nInstala con: pip install {' '.join(faltantes)}")
        return False
    
    return True

if __name__ == "__main__":
    # Verificar dependencias antes de ejecutar
    if not verificar_dependencias():
        print("\n💡 Instala las dependencias y vuelve a ejecutar la prueba")
        sys.exit(1)
    
    # Ejecutar prueba principal
    main()