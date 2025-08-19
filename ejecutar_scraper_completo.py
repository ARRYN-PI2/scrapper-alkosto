#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script completo para ejecutar el Scraper de Alkosto
==================================================

Uso:
    python ejecutar_scraper_completo.py

Ejemplos:
    # Scraping básico de televisores (20 productos)
    python ejecutar_scraper_completo.py --categoria televisores --limite 20
    
    # Scraping masivo de celulares (100 productos)
    python ejecutar_scraper_completo.py --categoria celulares --limite 100
    
    # Scraping con delay personalizado
    python ejecutar_scraper_completo.py --categoria audifonos --limite 50 --delay 2.0
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Agregamos el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from AlkostoScraperHibrido import AlkostoScraperHibrido
from src.domain.entities.producto_generico import get_categoria_config


def crear_directorio_salida():
    """Crea directorios para guardar los datos extraídos."""
    directories = ['data', 'data/output', 'data/processed', 'data/raw', 'logs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def guardar_productos_json(productos: List[Any], categoria: str, timestamp: str):
    """Guarda los productos extraídos en formato JSON."""
    filename = f"data/output/alkosto_{categoria}_{timestamp}.json"
    
    # Convertir productos a diccionarios si son objetos
    productos_dict = []
    for producto in productos:
        if hasattr(producto, 'to_dict'):
            productos_dict.append(producto.to_dict())
        elif isinstance(producto, dict):
            productos_dict.append(producto)
        else:
            # Fallback para objetos que no tienen to_dict
            productos_dict.append(str(producto))
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'categoria': categoria,
            'timestamp_extraccion': timestamp,
            'total_productos': len(productos_dict),
            'productos': productos_dict
        }, f, ensure_ascii=False, indent=2)
    
    print(f"Datos guardados en: {filename}")
    return filename


def mostrar_resumen_productos(productos: List[Any]):
    """Muestra un resumen de los productos extraídos."""
    if not productos:
        print("No se encontraron productos")
        return
    
    print(f"\nRESUMEN DE EXTRACCIÓN")
    print(f"{'='*50}")
    print(f"Total de productos extraídos: {len(productos)}")
    
    # Estadísticas básicas
    precios = []
    marcas = set()
    
    for producto in productos:
        if hasattr(producto, 'precio') and producto.precio:
            precios.append(producto.precio)
        if hasattr(producto, 'marca') and producto.marca:
            marcas.add(producto.marca)
    
    if precios:
        print(f"Precio promedio: ${sum(precios)/len(precios):,.0f}")
        print(f"Precio mínimo: ${min(precios):,.0f}")
        print(f"Precio máximo: ${max(precios):,.0f}")
    
    if marcas:
        print(f"Marcas encontradas: {len(marcas)}")
        print(f"Top marcas: {', '.join(list(marcas)[:5])}")
    
    # Mostrar primeros 3 productos como ejemplo
    print(f"\nEJEMPLOS DE PRODUCTOS:")
    print(f"{'-'*50}")
    for i, producto in enumerate(productos[:3]):
        if hasattr(producto, 'nombre'):
            precio_str = f"${producto.precio:,.0f}" if hasattr(producto, 'precio') and producto.precio else "Sin precio"
            marca_str = producto.marca if hasattr(producto, 'marca') and producto.marca else "Sin marca"
            print(f"{i+1}. {producto.nombre[:60]}...")
            print(f"   💰 {precio_str} | 🏷️ {marca_str}")


def ejecutar_scraping(categoria: str, limite: int, delay: float = 1.0, modo_generico: bool = True, usar_filtro: bool = True):
    """
    Ejecuta el proceso completo de scraping.
    
    Args:
        categoria: Categoría a scrapear (televisores, celulares, etc.)
        limite: Número máximo de productos a extraer
        delay: Tiempo de espera entre requests (segundos)
        modo_generico: Si usar ProductoGenerico (True) o entidades específicas (False)
        usar_filtro: Si usar filtro de categoría para validar URLs
    """
    print(f"INICIANDO SCRAPING DE ALKOSTO")
    print(f"{'='*50}")
    print(f" Categoría: {categoria}")
    print(f" Límite de productos: {limite}")
    print(f" Delay entre requests: {delay}s")
    print(f" Modo genérico: {'Sí' if modo_generico else 'No'}")
    print(f" Filtro de categoría: {'Activado' if usar_filtro else 'Desactivado'}")
    
    # Verificar configuración de categoría
    config = get_categoria_config(categoria)
    if not config:
        print(f" Error: Categoría '{categoria}' no está configurada")
        print(" Categorías disponibles: televisores, celulares, domotica, lavado, refrigeracion, cocina, audifonos, videojuegos, deportes")
        return None
    
    print(f" URL base: {config['url']}")
    print(f" Productos esperados: {config.get('max_productos_esperados', 'No especificado')}")
    
    try:
        # Crear scraper
        print(f"Inicializando scraper...")
        scraper = AlkostoScraperHibrido(
            categoria=categoria,
            modo_generico=modo_generico,
            delay_between_requests=delay,
            usar_filtro_categoria=usar_filtro
        )
        
        # Obtener URLs de productos
        print(f"Buscando URLs de productos...")
        urls = scraper.get_product_urls_with_load_more(max_productos=limite)
        
        if not urls:
            print(f" No se encontraron URLs de productos para la categoría '{categoria}'")
            return None
        
        print(f" Se encontraron {len(urls)} URLs de productos")
        
        # Extraer datos de cada producto
        print(f"Extrayendo datos de productos...")
        productos = []
        errores = 0
        
        for i, url in enumerate(urls, 1):
            try:
                print(f"   Procesando {i}/{len(urls)}: {url[:60]}...")
                producto = scraper.scrape_product(url)
                if producto:
                    productos.append(producto)
                    print(f"    Producto extraído exitosamente")
                else:
                    print(f"    No se pudo extraer el producto")
                    errores += 1
            except Exception as e:
                print(f"    Error extrayendo producto: {str(e)[:100]}")
                errores += 1
                continue
        
        # Guardar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if productos:
            archivo_salida = guardar_productos_json(productos, categoria, timestamp)
            mostrar_resumen_productos(productos)
            
            print(f"\n🎉 EXTRACCIÓN COMPLETADA")
            print(f"{'='*50}")
            print(f" Productos extraídos exitosamente: {len(productos)}")
            print(f" Errores durante extracción: {errores}")
            print(f" Archivo de salida: {archivo_salida}")
            
            return productos
        else:
            print(f"\n EXTRACCIÓN FALLIDA")
            print(f"No se pudo extraer ningún producto válido")
            return None
            
    except Exception as e:
        print(f"\n ERROR CRÍTICO: {str(e)}")
        return None


def main():
    """Función principal con argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Scraper de productos de Alkosto",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python ejecutar_scraper_completo.py --categoria televisores --limite 20
  python ejecutar_scraper_completo.py --categoria celulares --limite 50 --delay 1.5
  python ejecutar_scraper_completo.py --categoria audifonos --limite 30 --no-generico
        """
    )
    
    parser.add_argument(
        '--categoria', '-c',
        default='televisores',
        help='Categoría a scrapear (default: televisores)'
    )
    
    parser.add_argument(
        '--limite', '-l',
        type=int,
        default=20,
        help='Número máximo de productos a extraer (default: 20)'
    )
    
    parser.add_argument(
        '--delay', '-d',
        type=float,
        default=1.0,
        help='Tiempo de espera entre requests en segundos (default: 1.0)'
    )
    
    parser.add_argument(
        '--no-generico',
        action='store_true',
        help='Usar entidades específicas en lugar de ProductoGenerico'
    )
    
    parser.add_argument(
        '--sin-filtro',
        action='store_true',
        help='Desactivar filtro de categoría (extraer todos los productos encontrados)'
    )
    
    parser.add_argument(
        '--listar-categorias',
        action='store_true',
        help='Mostrar categorías disponibles y salir'
    )
    
    args = parser.parse_args()
    
    # Crear directorios necesarios
    crear_directorio_salida()
    
    # Mostrar categorías disponibles
    if args.listar_categorias:
        print(" CATEGORÍAS DISPONIBLES:")
        print("="*30)
        categorias = ['televisores', 'celulares', 'domotica', 'lavado', 'refrigeracion', 
                     'cocina', 'audifonos', 'videojuegos', 'deportes']
        for cat in categorias:
            config = get_categoria_config(cat)
            max_productos = config.get('max_productos_esperados', 'N/A') if config else 'N/A'
            print(f"  • {cat:<15} (max recomendado: {max_productos})")
        return
    
    # Validar límite
    if args.limite <= 0:
        print(" Error: El límite debe ser mayor que 0")
        return
    
    if args.limite > 500:
        print(" Advertencia: Límite muy alto, esto puede tomar mucho tiempo")
        respuesta = input("¿Continuar? (s/n): ").lower().strip()
        if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
            print(" Operación cancelada")
            return
    
    # Ejecutar scraping
    modo_generico = not args.no_generico
    usar_filtro = not args.sin_filtro
    productos = ejecutar_scraping(
        categoria=args.categoria,
        limite=args.limite,
        delay=args.delay,
        modo_generico=modo_generico,
        usar_filtro=usar_filtro
    )
    
    if productos is None:
        sys.exit(1)


if __name__ == "__main__":
    main()
