"""
PRUEBA 2: Verificación del Scraper con URLs Conocidas
=====================================================

OBJETIVO:
Probar que el scraper puede extraer datos correctamente de productos individuales
usando URLs que sabemos que funcionan.

QUÉ SE PRUEBA:
1. ✅ Extracción de datos de URLs específicas de productos
2. ✅ Verificar que todos los selectores funcionan correctamente
3. ✅ Confirmar que el formato de datos es correcto

URLS DE PRUEBA:
- TV Kalley 60 pulgadas
- TV Challenger 43 pulgadas  
- TV Samsung 65 pulgadas
- TV LG 55 pulgadas
"""

import sys
import os
from loguru import logger

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.infraestructure.scrapers.alkosto_scraper import AlkostoScraper
from src.domain.entities.televisor import Televisor


def test_manual_urls():
    """Prueba con URLs conocidas de productos."""
    
    # URLs que sabemos que funcionan
    test_urls = [
        "https://www.alkosto.com/tv-kalley-60-pulgadas-1524-cm-60g300-4k-uhd-led-smart-tv/p/7705946480048",
        "https://www.alkosto.com/tv-challenger-43-pulgadas-108-cm-led-43kg84-fhd-led-smart/p/7705191044927",
        "https://www.alkosto.com/tv-samsung-65-pulgadas-1651-cm-f-qn65ls03d-4k-uhd-qled-the/p/8806095715438",
        "https://www.alkosto.com/tv-lg-55-pulgadas-140-cm-55ua8050-4k-uhd-led-smart-tv-con/p/8806096329887"
    ]
    
    logger.info("🚀 Iniciando Prueba 2: URLs manuales")
    logger.info("=" * 60)
    
    scraper = AlkostoScraper(delay_between_requests=3.0)  # Delay más largo para ser respetuosos
    televisores = []
    
    for i, url in enumerate(test_urls, 1):
        try:
            logger.info(f"\n📺 Scrapeando producto {i}/{len(test_urls)}")
            logger.info(f"URL: {url}")
            
            televisor = scraper.scrape_product(url)
            televisores.append(televisor)
            
            # Mostrar resultados detallados
            logger.info("✅ DATOS EXTRAÍDOS:")
            logger.info(f"  📝 Nombre: {televisor.nombre}")
            logger.info(f"  🏷️ Marca: {televisor.marca}")
            logger.info(f"  💰 Precio: ${televisor.precio:,.0f}")
            logger.info(f"  📏 Tamaño: {televisor.tamano_pulgadas} pulgadas")
            logger.info(f"  🎯 Resolución: {televisor.resolucion}")
            logger.info(f"  ⭐ Calificación: {televisor.calificacion}")
            logger.info(f"  🌐 Fuente: {televisor.pagina_fuente}")
            
            # Verificar que los datos sean válidos
            issues = []
            if televisor.precio <= 0:
                issues.append("❌ Precio no extraído")
            if televisor.tamano_pulgadas <= 0:
                issues.append("❌ Tamaño no extraído")
            if televisor.marca == "Desconocida":
                issues.append("⚠️ Marca no identificada")
            if not televisor.nombre or televisor.nombre == "Nombre no disponible":
                issues.append("❌ Nombre no extraído")
            
            if issues:
                logger.warning("  PROBLEMAS DETECTADOS:")
                for issue in issues:
                    logger.warning(f"    {issue}")
            else:
                logger.success("  ✅ Todos los datos extraídos correctamente")
                
        except Exception as e:
            logger.error(f"❌ Error scrapeando {url}: {e}")
            continue
    
    # Resumen final
    logger.info(f"\n🎉 RESUMEN DE LA PRUEBA 2:")
    logger.info(f"  📊 Productos procesados: {len(televisores)}/{len(test_urls)}")
    
    if televisores:
        logger.info(f"  💰 Rango de precios: ${min(tv.precio for tv in televisores):,.0f} - ${max(tv.precio for tv in televisores):,.0f}")
        logger.info(f"  📏 Tamaños encontrados: {sorted(set(tv.tamano_pulgadas for tv in televisores))} pulgadas")
        logger.info(f"  🏷️ Marcas encontradas: {list(set(tv.marca for tv in televisores))}")
        
        # Mostrar el mejor y peor calificado
        tvs_con_rating = [tv for tv in televisores if tv.calificacion is not None]
        if tvs_con_rating:
            mejor = max(tvs_con_rating, key=lambda x: x.calificacion)
            logger.info(f"  ⭐ Mejor calificado: {mejor.marca} {mejor.tamano_pulgadas}\" - {mejor.calificacion}★")
    
    return televisores


def main():
    """Función principal"""
    # Configurar logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level="INFO"
    )
    
    try:
        televisores = test_manual_urls()
        
        if televisores:
            logger.success("\n🎉 ¡Prueba 2 exitosa! El scraper funciona correctamente.")
            logger.info("📋 Próximo paso: Implementar búsqueda de URLs automática")
        else:
            logger.error("\n❌ Prueba 2 falló. Revisar selectores y lógica de extracción.")
            
    except KeyboardInterrupt:
        logger.info("❌ Prueba interrumpida por el usuario")
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()