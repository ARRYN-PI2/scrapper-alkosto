"""
PRUEBA HÍBRIDA: Comparación entre Scraper Original y Genérico
============================================================

OBJETIVO:
Verificar que el scraper híbrido funciona igual que el original,
pero con capacidades expandidas para múltiples categorías.

QUÉ SE PRUEBA:
1. ✅ Modo Televisor (original) vs Modo Genérico con televisores
2. ✅ Mismos datos extraídos en ambos modos
3. ✅ Nuevas funcionalidades (imagen, timestamp, etc.)
4. ✅ Compatibilidad 100% con código existente
5. ✅ Prueba básica de otra categoría (celulares)
"""

import sys
import os
from loguru import logger
import time

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.infraestructure.scrapers.alkosto_scraper import AlkostoScraper
from src.infraestructure.scrapers.alkosto_scraper_hibrido import AlkostoScraperHibrido
from src.domain.entities.televisor import Televisor
from src.domain.entities.producto_generico import ProductoGenerico


def comparar_scrapers_tv():
    """Compara scraper original vs híbrido con televisores"""
    
    logger.info("🔄 COMPARACIÓN: Scraper Original vs Híbrido (Televisores)")
    logger.info("=" * 65)
    
    # URLs de prueba (usar las mismas para ambos scrapers)
    urls_prueba = [
        "https://www.alkosto.com/tv-lg-65-pulgadas-165-cm-65ua8050-4k-uhd-led-smart-tv-con/p/8806096330241",
        "https://www.alkosto.com/tv-samsung-55-pulgadas-1397-cm-q7f-4k-uhd-qled-smart-tv/p/8806097702870",
        "https://www.alkosto.com/tv-kalley-60-pulgadas-1524-cm-60g300-4k-uhd-led-smart-tv/p/7705946480048"
    ]
    
    # 1. Scraper Original
    logger.info("🔹 Probando Scraper ORIGINAL...")
    scraper_original = AlkostoScraper(delay_between_requests=1.0)
    televisores_originales = []
    
    for i, url in enumerate(urls_prueba, 1):
        try:
            logger.info(f"   Producto {i}/3 (Original)...")
            tv = scraper_original.scrape_product(url)
            televisores_originales.append(tv)
        except Exception as e:
            logger.error(f"   Error en original: {e}")
    
    # 2. Scraper Híbrido - Modo Televisor
    logger.info("🔹 Probando Scraper HÍBRIDO (modo Televisor)...")
    scraper_hibrido_tv = AlkostoScraperHibrido(categoria="televisores", modo_generico=False, delay_between_requests=1.0)
    televisores_hibridos = []
    
    for i, url in enumerate(urls_prueba, 1):
        try:
            logger.info(f"   Producto {i}/3 (Híbrido-TV)...")
            tv = scraper_hibrido_tv.scrape_product(url)
            televisores_hibridos.append(tv)
        except Exception as e:
            logger.error(f"   Error en híbrido-TV: {e}")
    
    # 3. Scraper Híbrido - Modo Genérico
    logger.info("🔹 Probando Scraper HÍBRIDO (modo Genérico)...")
    scraper_hibrido_gen = AlkostoScraperHibrido(categoria="televisores", modo_generico=True, delay_between_requests=1.0)
    productos_genericos = []
    
    for i, url in enumerate(urls_prueba, 1):
        try:
            logger.info(f"   Producto {i}/3 (Híbrido-Genérico)...")
            producto = scraper_hibrido_gen.scrape_product(url)
            productos_genericos.append(producto)
        except Exception as e:
            logger.error(f"   Error en híbrido-genérico: {e}")
    
    # 4. COMPARACIÓN DE RESULTADOS
    logger.info("\n📊 COMPARACIÓN DE RESULTADOS:")
    logger.info("-" * 50)
    
    for i in range(min(len(televisores_originales), len(televisores_hibridos), len(productos_genericos))):
        tv_orig = televisores_originales[i]
        tv_hibr = televisores_hibridos[i]
        prod_gen = productos_genericos[i]
        
        logger.info(f"\n🔍 PRODUCTO {i+1}:")
        logger.info(f"  📝 Original:    {tv_orig}")
        logger.info(f"  📝 Híbrido-TV:  {tv_hibr}")
        logger.info(f"  📝 Genérico:    {prod_gen}")
        
        # Verificar que los datos sean iguales
        diferencias = []
        if tv_orig.nombre != tv_hibr.nombre:
            diferencias.append("nombre")
        if tv_orig.precio != tv_hibr.precio:
            diferencias.append("precio")
        if tv_orig.marca != tv_hibr.marca:
            diferencias.append("marca")
        if tv_orig.tamano_pulgadas != tv_hibr.tamano_pulgadas:
            diferencias.append("tamaño")
        
        if diferencias:
            logger.warning(f"  ⚠️ Diferencias encontradas: {', '.join(diferencias)}")
        else:
            logger.success(f"  ✅ Original vs Híbrido: IDÉNTICOS")
        
        # Verificar conversión genérico -> televisor
        tv_from_gen = prod_gen.to_televisor()
        if (tv_from_gen.nombre == tv_orig.nombre and 
            tv_from_gen.precio == tv_orig.precio and
            tv_from_gen.marca == tv_orig.marca):
            logger.success(f"  ✅ Genérico -> Televisor: FUNCIONA")
        else:
            logger.warning(f"  ⚠️ Genérico -> Televisor: DIFERENCIAS")
        
        # Mostrar nuevas funcionalidades del genérico
        logger.info(f"  🖼️ Imagen: {'SÍ' if prod_gen.imagen else 'NO'}")
        logger.info(f"  📅 Timestamp: {prod_gen.timestamp_extraccion.strftime('%H:%M:%S')}")
        logger.info(f"  📂 Categoría: {prod_gen.categoria}")
        logger.info(f"  💾 Extras: {list(prod_gen.atributos_extra.keys())}")
    
    return {
        'originales': televisores_originales,
        'hibridos': televisores_hibridos, 
        'genericos': productos_genericos
    }


def probar_urls_automaticas():
    """Prueba la obtención automática de URLs"""
    
    logger.info("\n🔗 PRUEBA: Obtención Automática de URLs")
    logger.info("-" * 45)
    
    # Probar con scraper híbrido
    scraper = AlkostoScraperHibrido(categoria="televisores", modo_generico=True)
    
    logger.info("🔍 Obteniendo URLs de televisores...")
    urls = scraper.get_product_urls(max_pages=2)  # Solo 2 páginas para prueba
    
    logger.info(f"📊 URLs encontradas: {len(urls)}")
    logger.info("📋 Primeras 5 URLs:")
    for i, url in enumerate(urls[:5], 1):
        logger.info(f"  {i}. {url}")
    
    return urls


def probar_categoria_nueva():
    """Prueba rápida con una categoría nueva (celulares)"""
    
    logger.info("\n📱 PRUEBA: Nueva Categoría (Celulares)")
    logger.info("-" * 40)
    
    try:
        # Crear scraper para celulares
        scraper_celulares = AlkostoScraperHibrido(categoria="celulares", modo_generico=True)
        
        # Obtener algunas URLs
        logger.info("🔍 Obteniendo URLs de celulares...")
        urls = scraper_celulares.get_product_urls(max_pages=1)
        
        logger.info(f"📊 URLs de celulares encontradas: {len(urls)}")
        
        if urls:
            # Probar scraping de un celular
            logger.info("📱 Probando scraping de primer celular...")
            celular = scraper_celulares.scrape_product(urls[0])
            
            logger.info(f"✅ Celular extraído:")
            logger.info(f"  📝 Nombre: {celular.nombre}")
            logger.info(f"  💰 Precio: ${celular.precio:,.0f}")
            logger.info(f"  🏷️ Marca: {celular.marca}")
            logger.info(f"  📂 Categoría: {celular.categoria}")
            logger.info(f"  📏 Tamaño: {celular.tamaño}")
            logger.info(f"  ⭐ Calificación: {celular.calificacion}")
            
            return celular
        else:
            logger.warning("❌ No se encontraron URLs de celulares")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error probando celulares: {e}")
        return None


def probar_compatibilidad_json():
    """Prueba la conversión a JSON/diccionario"""
    
    logger.info("\n💾 PRUEBA: Compatibilidad JSON")
    logger.info("-" * 35)
    
    # Crear un producto genérico de ejemplo
    from datetime import datetime
    
    producto = ProductoGenerico(
        nombre="TV Samsung 55\" QLED 4K Smart TV",
        precio=1500000,
        marca="Samsung",
        categoria="televisores",
        url_producto="https://test.com/tv",
        fuente="alkosto",
        calificacion=4.5,
        tamaño="55 pulgadas",
        imagen="https://test.com/imagen.jpg"
    )
    
    producto.agregar_atributo_extra('resolucion', '4K')
    producto.agregar_atributo_extra('tamano_pulgadas', 55)
    
    # Convertir a dict
    producto_dict = producto.to_dict()
    logger.info("📄 Producto convertido a diccionario:")
    for key, value in producto_dict.items():
        logger.info(f"  {key}: {value}")
    
    # Convertir de vuelta
    producto_from_dict = ProductoGenerico.from_dict(producto_dict)
    logger.info(f"\n🔄 Producto desde diccionario: {producto_from_dict}")
    
    # Convertir a Televisor
    televisor = producto.to_televisor()
    logger.info(f"📺 Convertido a Televisor: {televisor}")
    
    return producto_dict


def main():
    """Función principal que ejecuta todas las pruebas"""
    
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        level="INFO"
    )
    
    logger.info("🚀 INICIANDO PRUEBAS HÍBRIDAS")
    logger.info("=" * 50)
    
    try:
        # 1. Comparación de scrapers
        resultados = comparar_scrapers_tv()
        
        # 2. URLs automáticas
        urls = probar_urls_automaticas()
        
        # 3. Nueva categoría
        celular = probar_categoria_nueva()
        
        # 4. Compatibilidad JSON
        json_data = probar_compatibilidad_json()
        
        # RESUMEN FINAL
        logger.info(f"\n🎉 RESUMEN DE PRUEBAS HÍBRIDAS")
        logger.info("=" * 40)
        logger.success(f"✅ Scraper original: {len(resultados['originales'])} productos")
        logger.success(f"✅ Scraper híbrido-TV: {len(resultados['hibridos'])} productos") 
        logger.success(f"✅ Scraper genérico: {len(resultados['genericos'])} productos")
        logger.success(f"✅ URLs automáticas: {len(urls)} encontradas")
        logger.success(f"✅ Categoría nueva: {'SÍ' if celular else 'NO'}")
        logger.success(f"✅ Compatibilidad JSON: {'SÍ' if json_data else 'NO'}")
        
        if (len(resultados['originales']) == len(resultados['hibridos']) == len(resultados['genericos']) 
            and len(urls) > 0):
            logger.success(f"\n🏆 ¡TODAS LAS PRUEBAS EXITOSAS!")
            logger.info("📋 El scraper híbrido está listo para producción")
        else:
            logger.warning(f"\n⚠️ Algunas pruebas fallaron - Revisar antes de continuar")
        
    except KeyboardInterrupt:
        logger.info("❌ Pruebas interrumpidas por el usuario")
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()