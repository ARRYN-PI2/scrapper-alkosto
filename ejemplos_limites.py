#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplos de configuración de límites para el Scraper de Alkosto
==============================================================

Este archivo muestra todas las formas de configurar límites en el scraper.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from AlkostoScraperHibrido import AlkostoScraperHibrido
from src.domain.entities.producto_generico import get_categoria_config


def ejemplo_limites_basicos():
    """Ejemplo 1: Límites básicos por número de productos"""
    print("=" * 60)
    print("EJEMPLO 1: LÍMITES BÁSICOS")
    print("=" * 60)
    
    # Crear scraper para televisores
    scraper = AlkostoScraperHibrido("televisores")
    
    # Diferentes límites
    limites = [5, 10, 20, 50]
    
    for limite in limites:
        print(f"\n Probando límite de {limite} productos:")
        urls = scraper.get_product_urls_with_load_more(max_productos=limite)
        print(f"   URLs encontradas: {len(urls)}")


def ejemplo_limites_por_categoria():
    """Ejemplo 2: Límites recomendados por categoría"""
    print("\n" + "=" * 60)
    print("EJEMPLO 2: LÍMITES RECOMENDADOS POR CATEGORÍA")
    print("=" * 60)
    
    categorias = ['televisores', 'celulares', 'audifonos', 'videojuegos']
    
    for categoria in categorias:
        config = get_categoria_config(categoria)
        if config:
            max_recomendado = config.get('max_productos_esperados', 100)
            print(f"\n {categoria.upper()}:")
            print(f"   URL: {config['url']}")
            print(f"   Máximo recomendado: {max_recomendado} productos")
            print(f"   Límites sugeridos:")
            print(f"     • Prueba rápida: 5-10 productos")
            print(f"     • Muestreo medio: {min(50, max_recomendado//4)} productos")
            print(f"     • Extracción completa: {max_recomendado} productos")


def ejemplo_limites_temporales():
    """Ejemplo 3: Límites temporales con delays"""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: LÍMITES TEMPORALES (DELAYS)")
    print("=" * 60)
    
    print(" Configuraciones de delay recomendadas:")
    print("   • Scraping rápido (riesgo alto):  0.5 segundos")
    print("   • Scraping normal (recomendado):  1.0 segundos") 
    print("   • Scraping conservador:          2.0 segundos")
    print("   • Scraping muy lento:            5.0 segundos")
    
    # Ejemplo con delay personalizado
    scraper_lento = AlkostoScraperHibrido(
        categoria="televisores",
        delay_between_requests=2.0  # 2 segundos entre requests
    )
    print(f"\n Scraper creado con delay de {scraper_lento.delay} segundos")


def ejemplo_limites_automaticos():
    """Ejemplo 4: Límites automáticos basados en configuración"""
    print("\n" + "=" * 60)
    print("EJEMPLO 4: LÍMITES AUTOMÁTICOS")
    print("=" * 60)
    
    def obtener_limite_automatico(categoria: str, tipo: str = "muestreo") -> int:
        """
        Calcula límites automáticos basados en la categoría.
        
        Args:
            categoria: Categoría del producto
            tipo: "prueba", "muestreo", "completo"
        """
        config = get_categoria_config(categoria)
        if not config:
            return 20  # Límite por defecto
        
        max_esperado = config.get('max_productos_esperados', 100)
        
        if tipo == "prueba":
            return min(10, max_esperado // 10)
        elif tipo == "muestreo":
            return min(50, max_esperado // 4)
        elif tipo == "completo":
            return max_esperado
        else:
            return 20
    
    # Mostrar límites automáticos para diferentes categorías
    categorias = ['televisores', 'celulares', 'audifonos']
    tipos = ['prueba', 'muestreo', 'completo']
    
    for categoria in categorias:
        print(f"\n {categoria.upper()}:")
        for tipo in tipos:
            limite = obtener_limite_automatico(categoria, tipo)
            print(f"   {tipo.capitalize()}: {limite} productos")


def ejemplo_uso_completo():
    """Ejemplo 5: Uso completo con todos los límites configurados"""
    print("\n" + "=" * 60)
    print("EJEMPLO 5: USO COMPLETO CON LÍMITES")
    print("=" * 60)
    
    # Configuración completa
    config = {
        'categoria': 'televisores',
        'limite_productos': 15,
        'delay_segundos': 1.5,
        'modo_generico': True,
        'limite_paginas': 5,  # Límite implícito en el código
        'timeout_request': 30  # Timeout por request
    }
    
    print(" Configuración utilizada:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    try:
        # Crear scraper con configuración
        scraper = AlkostoScraperHibrido(
            categoria=config['categoria'],
            modo_generico=config['modo_generico'],
            delay_between_requests=config['delay_segundos']
        )
        
        print(f"\n🔍 Buscando productos...")
        urls = scraper.get_product_urls_with_load_more(
            max_productos=config['limite_productos']
        )
        
        print(f" URLs encontradas: {len(urls)}")
        
        if urls:
            print(f" Extrayendo primer producto como ejemplo...")
            producto = scraper.scrape_product(urls[0])
            
            if producto and hasattr(producto, 'nombre'):
                print(f"    Producto: {producto.nombre[:60]}...")
                if hasattr(producto, 'precio') and producto.precio:
                    print(f"    Precio: ${producto.precio:,.0f}")
        
    except Exception as e:
        print(f" Error: {str(e)}")


def mostrar_resumen_limites():
    """Muestra un resumen de todos los tipos de límites disponibles"""
    print("\n" + "=" * 60)
    print("RESUMEN: TIPOS DE LÍMITES DISPONIBLES")
    print("=" * 60)
    
    print("""
 LÍMITES DE CANTIDAD:
   • max_productos: Número máximo de productos a extraer
   • Rango recomendado: 5-500 productos
   • Límite por defecto: 20 productos

⏱ LÍMITES TEMPORALES:
   • delay_between_requests: Tiempo entre requests (segundos)
   • Rango recomendado: 0.5-5.0 segundos
   • Límite por defecto: 1.0 segundos

 LÍMITES DE PÁGINAS:
   • Máximo 10 páginas por búsqueda (hardcoded)
   • Previene bucles infinitos
   • Se aplica automáticamente

 LÍMITES DE RED:
   • timeout: 30 segundos por request
   • Reintentos: No implementados (se puede agregar)
   • Headers rotativos para evitar bloqueos

 LÍMITES POR CATEGORÍA:
   • Configurados en get_categoria_config()
   • Basados en el tamaño esperado del catálogo
   • Personalizables por categoría

 LÍMITES DE SEGURIDAD:
   • User-Agent rotativo
   • Delays automáticos
   • Manejo de errores HTTP
   • Limpieza de URLs para evitar duplicados
    """)


def main():
    """Ejecuta todos los ejemplos de límites"""
    print("🚀 EJEMPLOS DE CONFIGURACIÓN DE LÍMITES PARA ALKOSTO SCRAPER")
    
    # Ejecutar todos los ejemplos
    ejemplo_limites_basicos()
    ejemplo_limites_por_categoria()
    ejemplo_limites_temporales()
    ejemplo_limites_automaticos()
    ejemplo_uso_completo()
    mostrar_resumen_limites()
    
    print(f"\n ¡Ejemplos completados!")
    print(f" Para usar el scraper, ejecuta:")
    print(f"   python ejecutar_scraper.py")
    print(f"   python ejecutar_scraper_completo.py --help")


if __name__ == "__main__":
    main()
