#!/usr/bin/env python3

from alkosto_scraper.adapters.alkosto_scraper_adapter import AlkostoScraperAdapter
import json

def test_scraper():
    print("Testing Alkosto Scraper...")
    
    # Inicializar el scraper
    scraper = AlkostoScraperAdapter()
    
    # Probar con una página de televisores
    print("Scraping televisores page 1...")
    productos = list(scraper.scrape("televisores", 1))
    
    print(f"Found {len(productos)} products")
    
    if productos:
        # Mostrar el primer producto para verificar
        producto = productos[0]
        print(f"\nPrimer producto:")
        print(f"Título: {producto.titulo}")
        print(f"Marca: {producto.marca}")
        print(f"Precio: {producto.precio_texto}")
        print(f"Link: {producto.link}")
        print(f"Detalles adicionales (primeros 200 chars): {producto.detalles_adicionales[:200]}...")
        
        # Convertir a dict para visualizar mejor
        producto_dict = {
            "titulo": producto.titulo,
            "marca": producto.marca,
            "precio_texto": producto.precio_texto,
            "precio_valor": producto.precio_valor,
            "tamaño": producto.tamaño,
            "detalles_adicionales": producto.detalles_adicionales,
            "link": producto.link
        }
        
        print(f"\nProducto completo en formato JSON:")
        print(json.dumps(producto_dict, indent=2, ensure_ascii=False))
    
    return productos

if __name__ == "__main__":
    productos = test_scraper()
