"""
PRUEBA 3: Escalabilidad del Scraper de Alkosto
==============================================

OBJETIVO:
Probar qué tan bien escala el scraper con múltiples páginas y productos.
Evaluar rendimiento, estabilidad y capacidad de procesamiento masivo.

QUÉ SE PRUEBA:
1. ✅ Scraping de múltiples páginas (2-5 páginas)
2. ✅ Tiempo de procesamiento y eficiencia
3. ✅ Manejo de errores en productos individuales
4. ✅ Estabilidad del navegador con muchas peticiones
5. ✅ Diversidad de marcas y productos encontrados
6. ✅ Detección automática del final de páginas

RESULTADOS ESPERADOS:
- Encontrar 50-150 productos únicos
- Tiempo razonable por página (1-2 minutos)
- Alta tasa de éxito en extracción de datos
- Diversidad de marcas, precios y características
"""

import sys
import os
from loguru import logger
import time
from collections import Counter

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.infraestructure.scrapers.alkosto_scraper import AlkostoScraper
from src.domain.entities.televisor import Televisor


def test_escalabilidad():
    """Prueba de escalabilidad con múltiples páginas."""
    
    logger.info("🚀 Iniciando Prueba 3: Escalabilidad")
    logger.info("=" * 60)
    
    # Configuración de la prueba
    MAX_PAGES = 3  # Empezar con 3 páginas
    DELAY_BETWEEN_REQUESTS = 2.0  # Un poco más lento para ser respetuosos
    
    scraper = AlkostoScraper(delay_between_requests=DELAY_BETWEEN_REQUESTS)
    
    # Fase 1: Obtener URLs de múltiples páginas
    logger.info(f"📄 FASE 1: Obteniendo URLs de {MAX_PAGES} páginas")
    start_time = time.time()
    
    product_urls = scraper.get_product_urls(max_pages=MAX_PAGES)
    
    urls_time = time.time() - start_time
    logger.info(f"⏱️ Tiempo para obtener URLs: {urls_time:.1f} segundos")
    logger.info(f"📊 URLs encontradas: {len(product_urls)}")
    logger.info(f"⚡ Promedio: {len(product_urls)/urls_time:.1f} URLs/segundo")
    
    if len(product_urls) == 0:
        logger.error("❌ No se encontraron URLs. Prueba fallida.")
        return
    
    # Mostrar muestra de URLs encontradas
    logger.info(f"\n📋 Muestra de URLs encontradas:")
    for i, url in enumerate(product_urls[:10], 1):
        logger.info(f"  {i}. {url}")
    if len(product_urls) > 10:
        logger.info(f"  ... y {len(product_urls) - 10} URLs más")
    
    # Fase 2: Scrapear una muestra representativa de productos
    logger.info(f"\n📺 FASE 2: Scrapeando muestra de productos")
    
    # Tomar una muestra para no saturar (máximo 20 productos para la prueba)
    sample_size = min(20, len(product_urls))
    sample_urls = product_urls[:sample_size]
    
    logger.info(f"🎯 Procesando muestra de {sample_size} productos...")
    
    televisores = []
    errores = []
    start_scraping = time.time()
    
    for i, url in enumerate(sample_urls, 1):
        try:
            logger.info(f"📺 Producto {i}/{sample_size}: Procesando...")
            
            product_start = time.time()
            televisor = scraper.scrape_product(url)
            product_time = time.time() - product_start
            
            televisores.append(televisor)
            
            # Log resumido para no saturar
            logger.info(f"  ✅ {televisor.marca} {televisor.tamano_pulgadas}\" - ${televisor.precio:,.0f} ({product_time:.1f}s)")
            
        except Exception as e:
            errores.append({'url': url, 'error': str(e)})
            logger.warning(f"  ❌ Error: {str(e)[:50]}...")
            continue
    
    scraping_time = time.time() - start_scraping
    
    # Fase 3: Análisis de resultados
    logger.info(f"\n📊 FASE 3: Análisis de resultados")
    logger.info("=" * 60)
    
    # Estadísticas básicas
    total_productos = len(televisores)
    tasa_exito = (total_productos / sample_size) * 100 if sample_size > 0 else 0
    
    logger.info(f"📈 ESTADÍSTICAS GENERALES:")
    logger.info(f"  📄 Páginas procesadas: {MAX_PAGES}")
    logger.info(f"  🔗 URLs encontradas: {len(product_urls)}")
    logger.info(f"  📺 Productos procesados: {total_productos}/{sample_size}")
    logger.info(f"  ✅ Tasa de éxito: {tasa_exito:.1f}%")
    logger.info(f"  ⏱️ Tiempo total scraping: {scraping_time:.1f} segundos")
    logger.info(f"  ⚡ Promedio por producto: {scraping_time/sample_size:.1f} segundos")
    
    if televisores:
        # Análisis de marcas
        marcas = Counter(tv.marca for tv in televisores)
        logger.info(f"\n🏷️ MARCAS ENCONTRADAS:")
        for marca, cantidad in marcas.most_common():
            logger.info(f"  {marca}: {cantidad} productos")
        
        # Análisis de precios
        precios = [tv.precio for tv in televisores if tv.precio > 0]
        if precios:
            logger.info(f"\n💰 ANÁLISIS DE PRECIOS:")
            logger.info(f"  Menor: ${min(precios):,.0f}")
            logger.info(f"  Mayor: ${max(precios):,.0f}")
            logger.info(f"  Promedio: ${sum(precios)/len(precios):,.0f}")
        
        # Análisis de tamaños
        tamanos = Counter(tv.tamano_pulgadas for tv in televisores if tv.tamano_pulgadas > 0)
        logger.info(f"\n📏 TAMAÑOS ENCONTRADOS:")
        for tamano, cantidad in sorted(tamanos.items()):
            logger.info(f"  {tamano}\": {cantidad} productos")
        
        # Análisis de resoluciones
        resoluciones = Counter(tv.resolucion for tv in televisores)
        logger.info(f"\n🎯 RESOLUCIONES:")
        for resolucion, cantidad in resoluciones.most_common():
            logger.info(f"  {resolucion}: {cantidad} productos")
    
    # Análisis de errores
    if errores:
        logger.warning(f"\n❌ ERRORES ENCONTRADOS ({len(errores)}):")
        for error in errores[:5]:  # Mostrar solo los primeros 5
            logger.warning(f"  - {error['error'][:80]}...")
    
    # Proyección de escalabilidad
    logger.info(f"\n🚀 PROYECCIÓN DE ESCALABILIDAD:")
    if len(product_urls) > 0 and scraping_time > 0:
        tiempo_por_producto = scraping_time / sample_size
        productos_totales_estimados = len(product_urls)
        tiempo_total_estimado = productos_totales_estimados * tiempo_por_producto / 60  # en minutos
        
        logger.info(f"  📊 Productos totales disponibles: ~{productos_totales_estimados}")
        logger.info(f"  ⏱️ Tiempo estimado para todos: ~{tiempo_total_estimado:.1f} minutos")
        logger.info(f"  💡 Productos por hora: ~{3600/tiempo_por_producto:.0f}")
    
    # Recomendaciones
    logger.info(f"\n💡 RECOMENDACIONES:")
    if tasa_exito >= 90:
        logger.success("  ✅ Excelente estabilidad - Listo para producción")
    elif tasa_exito >= 75:
        logger.info("  ⚠️ Buena estabilidad - Algunos ajustes menores")
    else:
        logger.warning("  ❌ Revisar manejo de errores antes de producción")
    
    tiempo_por_producto = scraping_time / sample_size if sample_size > 0 else 0
    if tiempo_por_producto < 2:
        logger.success("  ✅ Velocidad excelente")
    elif tiempo_por_producto < 5:
        logger.info("  ⚡ Velocidad aceptable")
    else:
        logger.warning("  ⏳ Considerar optimizaciones de velocidad")
    
    return {
        'total_urls': len(product_urls),
        'productos_procesados': total_productos,
        'tasa_exito': tasa_exito,
        'tiempo_scraping': scraping_time,
        'marcas_encontradas': len(marcas) if televisores else 0,
        'televisores': televisores
    }


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
        resultados = test_escalabilidad()
        
        logger.info(f"\n🎉 PRUEBA 3 COMPLETADA")
        logger.info("=" * 60)
        
        if resultados['tasa_exito'] >= 75:
            logger.success("✅ Scraper aprobó la prueba de escalabilidad")
            logger.info("📋 Listo para implementar guardado en JSON y MongoDB")
        else:
            logger.warning("⚠️ Scraper necesita ajustes antes de producción")
        
        # Pregunta sobre continuar con scraping completo
        if resultados['total_urls'] > 20:
            respuesta = input(f"\n¿Quieres probar scraping completo de todos los {resultados['total_urls']} productos? (puede tardar mucho) [y/N]: ")
            if respuesta.lower() in ['y', 'yes', 'sí', 'si']:
                logger.info("🚀 Iniciando scraping completo...")
                scraper = AlkostoScraper(delay_between_requests=1.5)
                todos_los_televisores = scraper.scrape_all_products(max_pages=3)
                logger.success(f"🎉 Scraping completo: {len(todos_los_televisores)} productos extraídos")
            else:
                logger.info("📋 Continuando con el siguiente paso del proyecto")
        
    except KeyboardInterrupt:
        logger.info("❌ Prueba interrumpida por el usuario")
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()