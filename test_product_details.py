#!/usr/bin/env python3

from alkosto_scraper.adapters.alkosto_scraper_adapter import AlkostoScraperAdapter
import json

def test_product_details():
    print("Testing product details extraction...")
    
    # Inicializar el scraper
    scraper = AlkostoScraperAdapter()
    
    # URL del producto específico
    product_url = "https://www.alkosto.com/tv-tcl-55-pulgadas-139-cm-55a300w-4k-uhd-qled-art-tv-smart/p/6921732899547"
    
    print(f"Extracting details from: {product_url}")
    details = scraper._extract_product_details(product_url)
    
    print(f"Extracted details length: {len(details)} characters")
    print(f"Details preview (first 500 chars):")
    print(details[:500])
    print("\n" + "="*80 + "\n")
    print("Full details:")
    print(details)

if __name__ == "__main__":
    test_product_details()
