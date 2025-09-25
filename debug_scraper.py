#!/usr/bin/env python3

from alkosto_scraper.adapters.alkosto_scraper_adapter import AlkostoScraperAdapter
import json

def debug_scraper():
    print("Debugging scraper...")
    
    # Inicializar el scraper
    scraper = AlkostoScraperAdapter()
    
    # Probar con una página de televisores
    print("Scraping televisores page 1...")
    productos = list(scraper.scrape("televisores", 1))
    
    print(f"Found {len(productos)} products")
    
    for i, producto in enumerate(productos[:3]):  # Solo los primeros 3
        print(f"\nProducto {i+1}:")
        print(f"Título: {producto.titulo}")
        print(f"Link: {producto.link}")
        print(f"Detalles adicionales length: {len(producto.detalles_adicionales)}")
        if len(producto.detalles_adicionales) > 0:
            print(f"Detalles preview: {producto.detalles_adicionales[:200]}...")
        else:
            print("Sin detalles adicionales")
        
        # Check if it's a valid product URL
        if not producto.link.startswith("https://www.alkosto.com/") or "/p/" not in producto.link:
            print("❌ Not a product URL - likely a category link")
        else:
            print("✅ Valid product URL")

if __name__ == "__main__":
    debug_scraper()
