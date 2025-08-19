"""
PRUEBA 1: Verificación Básica del Scraper de Alkosto
====================================================

OBJETIVO:
Esta es la primera prueba del sistema de scraping. Su objetivo es verificar que todos 
los componentes básicos funcionen correctamente antes de avanzar a funcionalidades más complejas.

QUÉ SE PRUEBA:
1. ✅ Funcionalidad de la clase Televisor (creación, conversión a dict, etc.)
2. ✅ Capacidad del scraper para encontrar URLs de productos en Alkosto
3. ✅ Extracción de datos de un producto individual (nombre, precio, marca, etc.)
4. ✅ Proceso completo de scraping de múltiples productos (opcional)

RESULTADOS ESPERADOS:
- La clase Televisor debe crear objetos correctamente y convertir a/desde diccionarios
- El scraper debe encontrar al menos 10-20 URLs de productos de televisores
- Debe extraer correctamente: nombre, precio, marca, tamaño, resolución, calificación
- Los selectores CSS deben coincidir con la estructura actual de Alkosto

SI ESTA PRUEBA FALLA:
- Revisar conectividad a internet
- Verificar que los selectores CSS coincidan con la página actual de Alkosto
- Ajustar delays entre peticiones si hay problemas de rate limiting

PRÓXIMOS PASOS:
- Prueba 2: Limpieza y normalización de datos
- Prueba 3: Guardado en JSON
- Prueba 4: Integración con MongoDB
"""

import sys
import os
from loguru import logger

# Agregar el directorio src al path para poder importar nuestros módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.infraestructure.scrapers.alkosto_scraper import AlkostoScraper
from src.domain.entities.televisor import Televisor


def test_product_urls():
    """Prueba la extracción de URLs de productos."""
    logger.info("=== PRUEBA: Extracción de URLs de productos ===")
    
    scraper = AlkostoScraper(delay_between_requests=1.0)  # Delay corto para pruebas
    
    try:
        # Probar con solo 1 página para empezar
        urls = scraper.get_product_urls(max_pages=1)
        
        logger.info(f"URLs encontradas: {len(urls)}")
        for i, url in enumerate(urls[:5], 1):  # Mostrar solo las primeras 5
            logger.info(f"{i}. {url}")
        
        if len(urls) > 5:
            logger.info(f"... y {len(urls) - 5} URLs más")
        
        return urls[:3]  # Retornar solo 3 para pruebas
        
    except Exception as e:
        logger.error(f"Error en extracción de URLs: {e}")
        return []


def test_single_product(product_url: str):
    """Prueba la extracción de datos de un producto específico."""
    logger.info(f"=== PRUEBA: Scraping de producto individual ===")
    logger.info(f"URL: {product_url}")
    
    scraper = AlkostoScraper(delay_between_requests=1.0)
    
    try:
        televisor = scraper.scrape_product(product_url)
        
        logger.info("✅ Producto extraído exitosamente:")
        logger.info(f"  Nombre: {televisor.nombre}")
        logger.info(f"  Marca: {televisor.marca}")
        logger.info(f"  Precio: ${televisor.precio:,.0f}")
        logger.info(f"  Tamaño: {televisor.tamano_pulgadas} pulgadas")
        logger.info(f"  Resolución: {televisor.resolucion}")
        logger.info(f"  Calificación: {televisor.calificacion}")
        logger.info(f"  URL: {televisor.url_producto}")
        
        return televisor
        
    except Exception as e:
        logger.error(f"Error scrapeando producto: {e}")
        return None


def test_complete_scraping():
    """Prueba el scraping completo de múltiples productos."""
    logger.info("=== PRUEBA: Scraping completo ===")
    
    scraper = AlkostoScraper(delay_between_requests=2.0)
    
    try:
        # Scrapear solo 1 página con pocos productos para prueba
        televisores = scraper.scrape_all_products(max_pages=1)
        
        logger.info(f"✅ Scraping completado: {len(televisores)} televisores extraídos")
        
        # Mostrar resumen de los primeros productos
        for i, tv in enumerate(televisores[:3], 1):
            logger.info(f"{i}. {tv}")
        
        return televisores
        
    except Exception as e:
        logger.error(f"Error en scraping completo: {e}")
        return []


def test_televisor_methods():
    """Prueba los métodos de la clase Televisor."""
    logger.info("=== PRUEBA: Métodos de la clase Televisor ===")
    
    # Crear un televisor de prueba
    tv_test = Televisor(
        nombre="TV Samsung 55\" QLED 4K Smart TV",
        precio=1500000,
        tamano_pulgadas=55,
        calificacion=4.5,
        marca="Samsung",
        resolucion="4K",
        pagina_fuente="alkosto",
        url_producto="https://test.com/tv"
    )
    
    logger.info("Televisor de prueba creado:")
    logger.info(f"  String representation: {tv_test}")
    
    # Probar conversión a diccionario
    tv_dict = tv_test.to_dict()
    logger.info(f"  Diccionario: {tv_dict}")
    
    # Probar creación desde diccionario
    tv_from_dict = Televisor.from_dict(tv_dict)
    logger.info(f"  Desde diccionario: {tv_from_dict}")
    
    return tv_test


def main():
    """Función principal que ejecuta todas las pruebas."""
    logger.info("🚀 Iniciando pruebas del scraper de Alkosto")
    logger.info("=" * 60)
    
    # Configurar logging
    logger.remove()  # Remover handler por defecto
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level="INFO"
    )
    
    try:
        # 1. Probar métodos de la clase Televisor
        test_televisor_methods()
        logger.info("")
        
        # 2. Probar extracción de URLs
        urls = test_product_urls()
        logger.info("")
        
        if not urls:
            logger.error("❌ No se pudieron obtener URLs. Revisa la conexión y selectores.")
            return
        
        # 3. Probar scraping de un producto individual
        if urls:
            test_single_product(urls[0])
            logger.info("")
        
        # 4. Preguntar si continuar con scraping completo
        respuesta = input("¿Quieres probar el scraping completo? (puede tardar varios minutos) [y/N]: ")
        if respuesta.lower() in ['y', 'yes', 'sí', 'si']:
            test_complete_scraping()
        
        logger.info("🎉 Pruebas completadas")
        
    except KeyboardInterrupt:
        logger.info("❌ Pruebas interrumpidas por el usuario")
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()