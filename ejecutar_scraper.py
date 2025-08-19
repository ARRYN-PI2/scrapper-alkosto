#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script básico para ejecutar el Scraper de Alkosto
================================================

Uso rápido: Modifica las variables y ejecuta
"""

import sys
import os
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from AlkostoScraperHibrido import AlkostoScraperHibrido


def main():
    # ===== CONFIGURACIÓN BÁSICA =====
    CATEGORIA = "televisores"  # Cambiar por: celulares, audifonos, domotica, etc.
    LIMITE_PRODUCTOS = 10      # Número máximo de productos a extraer
    DELAY_SEGUNDOS = 1.0       # Tiempo de espera entre requests
    
    print(f" Iniciando scraping de {CATEGORIA}...")
    print(f" Límite: {LIMITE_PRODUCTOS} productos")
    
    try:
        # Crear scraper
        scraper = AlkostoScraperHibrido(
            categoria=CATEGORIA,
            modo_generico=True,  # Usar ProductoGenerico
            delay_between_requests=DELAY_SEGUNDOS
        )
        
        # Obtener URLs
        print(" Buscando productos...")
        urls = scraper.get_product_urls_with_load_more(max_productos=LIMITE_PRODUCTOS)
        print(f" Encontradas {len(urls)} URLs")
        
        # Extraer productos
        productos = []
        for i, url in enumerate(urls, 1):
            print(f" Extrayendo producto {i}/{len(urls)}...")
            try:
                producto = scraper.scrape_product(url)
                if producto:
                    productos.append(producto)
                    # Mostrar información básica
                    if hasattr(producto, 'nombre') and hasattr(producto, 'precio'):
                        print(f"    {producto.nombre[:50]}... - ${producto.precio:,.0f}")
                    else:
                        print(f"    Producto extraído")
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:50]}...")
        
        # Mostrar resumen
        print(f"\n COMPLETADO!")
        print(f" Total extraído: {len(productos)} productos")
        
        # Guardar en JSON (opcional)
        if productos:
            import json
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/alkosto_{CATEGORIA}_{timestamp}.json"
            
            # Crear directorio si no existe
            os.makedirs("data", exist_ok=True)
            
            # Convertir productos a diccionarios
            productos_dict = []
            for producto in productos:
                if hasattr(producto, 'to_dict'):
                    productos_dict.append(producto.to_dict())
                else:
                    productos_dict.append(str(producto))
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'categoria': CATEGORIA,
                    'timestamp': timestamp,
                    'total': len(productos_dict),
                    'productos': productos_dict
                }, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Guardado en: {filename}")
        
    except Exception as e:
        print(f"💥 ERROR: {e}")


if __name__ == "__main__":
    main()