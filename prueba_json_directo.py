#!/usr/bin/env python3
"""
prueba_json_directo.py - Prueba DIRECTA de guardado en JSON

FUNCIONALIDAD:
- Scraping rápido (pocos productos para probar)
- Guardado inmediato en JSON
- Sin procesamiento complejo (solo lo básico)

EJECUCIÓN:
python prueba_json_directo.py
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.infraestructure.scrapers.alkosto_scraper import AlkostoScraper
    from src.infraestructure.persistence.json_repository import JsonRepository
    from loguru import logger
except ImportError as e:
    print(f"❌ Error importando: {e}")
    print("💡 Verifica que tengas los archivos:")
    print("   - src/infraestructure/scrapers/alkosto_scraper.py")
    print("   - src/infraestructure/persistence/json_repository.py")
    sys.exit(1)

def main():
    print("🧪 PRUEBA DIRECTA: Scraping → JSON")
    print("="*50)
    print()
    print("📋 OPCIONES RÁPIDAS:")
    print("   [1] Solo 10 productos (2-3 min)")
    print("   [2] Solo 25 productos (5-7 min)")
    print("   [3] 50 productos (8-10 min)")
    print()
    
    opcion = input("Selecciona (1/2/3): ").strip()
    
    # Configurar cantidad según opción
    if opcion == "1":
        max_products = 10
    elif opcion == "2":
        max_products = 25
    elif opcion == "3":
        max_products = 50
    else:
        print("❌ Opción no válida")
        return
    
    print(f"\n🚀 Iniciando scraping de {max_products} productos...")
    
    # Configurar logging simple
    logger.remove()
    logger.add(sys.stdout, format="{time:HH:mm:ss} | {message}", level="INFO")
    
    try:
        # PASO 1: Crear instancias
        scraper = AlkostoScraper(delay_between_requests=0.5)  # Más rápido
        json_repo = JsonRepository()
        
        # PASO 2: Obtener URLs (solo las que necesitamos)
        print(f"\n📡 Obteniendo URLs...")
        
        # Para prueba rápida, podemos usar el método original si max_products <= 25
        if max_products <= 25:
            product_urls = scraper.get_product_urls(max_pages=1)  # Solo primera página
        else:
            product_urls = scraper.get_product_urls_with_load_more(max_products=max_products)
        
        # Limitar a la cantidad deseada
        product_urls = product_urls[:max_products]
        
        print(f"✅ URLs obtenidas: {len(product_urls)}")
        
        # PASO 3: Scrapear productos
        print(f"\n📦 Scrapeando productos...")
        televisores = []
        
        for i, url in enumerate(product_urls, 1):
            try:
                print(f"🔄 {i}/{len(product_urls)}: Scrapeando...")
                televisor = scraper.scrape_product(url)
                
                if televisor:
                    televisores.append(televisor)
                    print(f"   ✅ {televisor.marca} {televisor.tamano_pulgadas}\" - ${televisor.precio:,.0f}")
                else:
                    print(f"   ⚠️ Producto vacío")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n📊 Scraping completado: {len(televisores)} productos válidos")
        
        if not televisores:
            print("❌ No se obtuvieron productos. Terminando.")
            return
        
        # PASO 4: Guardar en JSON
        print(f"\n💾 Guardando en JSON...")
        archivo_json = json_repo.save_televisions(televisores, source="alkosto")
        
        # PASO 5: Verificar archivo
        file_size = Path(archivo_json).stat().st_size / 1024  # KB
        print(f"✅ Archivo guardado: {archivo_json}")
        print(f"📁 Tamaño: {file_size:.1f} KB")
        
        # PASO 6: Probar carga
        print(f"\n🔍 Verificando carga...")
        televisores_cargados = json_repo.load_televisions(archivo_json)
        print(f"✅ Carga verificada: {len(televisores_cargados)} productos")
        
        # PASO 7: Mostrar muestra del JSON
        print(f"\n📋 MUESTRA DE DATOS GUARDADOS:")
        info = json_repo.get_file_info(archivo_json)
        
        print(f"   📦 Total productos: {info['total_productos']}")
        print(f"   📅 Fecha: {info['fecha_scraping'][:19]}")
        
        if 'estadisticas' in info and info['estadisticas']:
            stats = info['estadisticas']
            precios = stats.get('precios', {})
            marcas = stats.get('marcas_top_5', {})
            
            if precios:
                print(f"   💰 Precio promedio: ${precios.get('promedio', 0):,.0f}")
            
            if marcas:
                top_marca = list(marcas.keys())[0] if marcas else "N/A"
                print(f"   🏆 Marca principal: {top_marca}")
        
        # PASO 8: Mostrar contenido del JSON (primeros productos)
        print(f"\n📄 PRIMEROS 3 PRODUCTOS EN JSON:")
        for i, tv in enumerate(televisores[:3], 1):
            print(f"   {i}. {tv.nombre[:40]}...")
            print(f"      Marca: {tv.marca} | Tamaño: {tv.tamano_pulgadas}\" | Precio: ${tv.precio:,.0f}")
            print(f"      URL: {tv.url_producto[:50]}...")
            print()
        
        print("🎉 ¡PRUEBA EXITOSA!")
        print(f"📁 Tu archivo JSON está en: {archivo_json}")
        print(f"💡 Puedes abrirlo con cualquier editor de texto")
        
    except KeyboardInterrupt:
        print("\n⏹️ Prueba interrumpida")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()