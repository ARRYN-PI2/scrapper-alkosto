"""
Script de diagnóstico para ver qué HTML está recibiendo el scraper
"""

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def debug_page():
    """Inspecciona el HTML real que recibe el scraper"""
    
    url = "https://www.alkosto.com/tv/smart-tv/c/BI_120_ALKOS"
    
    # Usar los mismos headers que el scraper
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    print("🔍 Haciendo petición a Alkosto...")
    response = requests.get(url, headers=headers, timeout=30)
    print(f"✅ Respuesta recibida. Status: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 1. Buscar todos los enlaces
    all_links = soup.find_all('a', href=True)
    print(f"\n📊 Total de enlaces encontrados: {len(all_links)}")
    
    # 2. Buscar enlaces que contengan '/p/'
    product_pattern_links = [link for link in all_links if link.get('href') and '/p/' in link.get('href')]
    print(f"📊 Enlaces con '/p/': {len(product_pattern_links)}")
    
    # 3. Buscar enlaces que empiecen con '/tv-'
    tv_links = [link for link in all_links if link.get('href') and link.get('href').startswith('/tv-')]
    print(f"📊 Enlaces que empiezan con '/tv-': {len(tv_links)}")
    
    # 4. Buscar la clase específica
    class_links = soup.find_all('a', class_='product__item__top__link')
    print(f"📊 Enlaces con clase 'product__item__top__link': {len(class_links)}")
    
    # 5. Mostrar algunos ejemplos de enlaces con /p/
    print(f"\n🔗 Primeros 5 enlaces con '/p/':")
    for i, link in enumerate(product_pattern_links[:5], 1):
        href = link.get('href')
        classes = link.get('class', [])
        print(f"  {i}. {href}")
        print(f"     Clases: {classes}")
        print()
    
    # 6. Buscar otras clases posibles relacionadas con productos
    print("🔍 Buscando otras clases que contengan 'product':")
    product_elements = soup.find_all(attrs={"class": lambda x: x and any('product' in cls for cls in x)})
    unique_classes = set()
    for elem in product_elements:
        if elem.name == 'a' and elem.get('href'):
            classes = elem.get('class', [])
            for cls in classes:
                if 'product' in cls:
                    unique_classes.add(cls)
    
    for cls in sorted(unique_classes):
        count = len(soup.find_all('a', class_=cls))
        if count > 0:
            print(f"  - {cls}: {count} elementos")
    
    # 7. Guardar una muestra del HTML para inspección
    with open('debug_alkosto.html', 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))
    print(f"\n💾 HTML guardado en 'debug_alkosto.html' para inspección manual")

if __name__ == "__main__":
    debug_page()