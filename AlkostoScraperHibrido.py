# src/infraestructure/scrapers/alkosto_scraper_hibrido.py
# -*- coding: utf-8 -*-
"""
Scraper Alkosto Híbrido
------------------------

Modo de uso:

    scraper = AlkostoScraperHibrido("televisores", modo_generico=True)
    urls = scraper.get_product_urls_with_load_more(max_productos=10)
    prod = scraper.scrape_product(urls[0])

Notas:
- Usa solo peticiones HTTP + BeautifulSoup (sin Selenium).
- Detecta URLs de producto por el patrón "/p/".
- La paginación intenta `?page=2` y como fallback `?p=2`.
- Parsing robusto para título, precio, marca, specs y metadatos.
- Mantiene compatibilidad con modo `modo_generico=False` para televisores.
"""
from __future__ import annotations

import re
import time
import random
import html
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs, urlencode

import requests
from bs4 import BeautifulSoup

# Selenium imports para contenido dinámico
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    import chromedriver_autoinstaller
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# --- Imports a entidades del dominio ---
try:
    # get_categoria_config es requerido por tu proyecto
    from src.domain.entities.producto_generico import (
        get_categoria_config,
        ProductoGenerico,
    )
except Exception:  # pragma: no cover
    # Si ProductoGenerico no está aquí, intentamos sólo importar la función
    from src.domain.entities.producto_generico import get_categoria_config  # type: ignore
    ProductoGenerico = None  # type: ignore

try:
    # Para compatibilidad con modo no genérico (televisores)
    from src.domain.entities.televisor import Televisor  # type: ignore
except Exception:  # pragma: no cover
    Televisor = None  # type: ignore


_DEFAULT_HEADERS = [
    # Lista corta rotativa de UAs para reducir bloqueos triviales
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
]


class AlkostoScraperHibrido:
    def __init__(
        self,
        categoria: str,
        modo_generico: bool = True,
        delay_between_requests: float = 1.0,
        session: Optional[requests.Session] = None,
        usar_filtro_categoria: bool = True,
    ) -> None:
        self.categoria: str = (categoria or "").strip().lower()
        self.modo_generico: bool = modo_generico
        self.delay: float = max(0.0, delay_between_requests)
        self.session: requests.Session = session or requests.Session()
        self.usar_filtro_categoria: bool = usar_filtro_categoria
        
        # Configuración para Selenium (para contenido dinámico)
        self.driver = None
        self.selenium_enabled = SELENIUM_AVAILABLE
        
        self.headers: Dict[str, str] = {
            "User-Agent": random.choice(_DEFAULT_HEADERS),
            "Accept-Language": "es-CO,es;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

        # Config preferida desde tu dominio (URL, límites, etc.)
        self.config: Dict = get_categoria_config(self.categoria) or {}
        self.base_url: str = self.config.get("url") or f"https://www.alkosto.com/{self.categoria}"
        
        # Imprimir configuración
        print(f"Categoría seleccionada: {self.categoria}")
        print(f"Base URL: {self.base_url}")
        print(f"Filtro de categoría: {'Activado' if self.usar_filtro_categoria else 'Desactivado'}")
        if self.config and self.usar_filtro_categoria:
            patrones = self.config.get('patron_url', [])
            print(f"Patrones de URL esperados: {patrones}")
        elif not self.config:
            print("No se encontró configuración para esta categoría")


        # Normalización por si la URL de config no trae esquema/host claramente
        if self.base_url.startswith("/"):
            self.base_url = urljoin("https://www.alkosto.com/", self.base_url)

    def __del__(self):
        """Limpieza automática del driver de Selenium."""
        self._close_selenium()

    # ------------------------
    # Utilitarios HTTP/tiempos
    # ------------------------
    def _sleep(self) -> None:
        if self.delay > 0:
            time.sleep(self.delay)

    def _get_html(self, url: str) -> str:
        self._sleep()
        resp = self.session.get(url, headers=self.headers, timeout=30)
        resp.raise_for_status()
        return resp.text

    def _init_selenium_driver(self):
        """Inicializa el driver de Selenium si está disponible."""
        if not self.selenium_enabled:
            print("Selenium no está disponible")
            return False
            
        if self.driver is not None:
            return True
            
        try:
            # Auto-instalar la versión correcta de ChromeDriver
            chromedriver_autoinstaller.install()
            
            options = Options()
            options.add_argument('--headless')  # Ejecutar sin ventana
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument(f'--user-agent={self.headers["User-Agent"]}')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("Selenium inicializado correctamente con ChromeDriver auto-instalado")
            return True
            
        except Exception as e:
            print(f"Error inicializando Selenium: {e}")
            self.selenium_enabled = False
            return False

    def _get_html_selenium(self, url: str) -> str:
        """Obtiene HTML usando Selenium para contenido dinámico."""
        if not self._init_selenium_driver():
            raise Exception("Selenium no está disponible")
            
        try:
            self._sleep()
            self.driver.get(url)
            
            # Esperar a que cargue el contenido
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Esperar un poco más para que cargue el JavaScript
            time.sleep(3)
            
            # Intentar hacer scroll para activar lazy loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            return self.driver.page_source
            
        except Exception as e:
            print(f"Error obteniendo HTML con Selenium: {e}")
            raise

    def _close_selenium(self):
        """Cierra el driver de Selenium."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

    # ------------------------
    # Listado / Paginación
    # ------------------------
    def _build_paged_url(self, base: str, page: int, param: str = "page") -> str:
        if page <= 1:
            return base
        parsed = urlparse(base)
        q = parse_qs(parsed.query)
        q[param] = [str(page)]
        new_query = urlencode({k: v[0] if isinstance(v, list) else v for k, v in q.items()})
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))

    def _extract_listing_urls(self, soup: BeautifulSoup) -> List[str]:
        # Patrón robusto: todos los <a> que lleven a "/p/"
        urls: List[str] = []
        for a in soup.select('a[href*="/p/"]'):
            href = a.get("href")
            if not href:
                continue
            full = urljoin(self.base_url, href)
            if "/p/" in full:
                # Validar que la URL corresponda a la categoría (si el filtro está activado)
                clean_url = self._strip_tracking(full)
                if not self.usar_filtro_categoria or self._is_valid_category_url(clean_url):
                    urls.append(clean_url)
                elif self.usar_filtro_categoria:
                    print(f"URL ignorada (no corresponde a categoría): {clean_url[:60]}...")
        
        # Si no encontramos URLs válidas pero hay patrones configurados, intentar búsqueda alternativa
        if not urls and self.config and self.config.get('patron_url'):
            print(f"  🔍 Intentando búsqueda alternativa de productos...")
            urls = self._extract_urls_alternative_search(soup)
        
        # Dedup conservando orden
        seen = set()
        dedup: List[str] = []
        for u in urls:
            if u not in seen:
                dedup.append(u)
                seen.add(u)
        return dedup

    def _strip_tracking(self, url: str) -> str:
        # Limpia parámetros para evitar duplicados
        p = urlparse(url)
        clean = urlunparse((p.scheme, p.netloc, p.path, p.params, "", ""))
        return clean

    def _is_valid_category_url(self, url: str) -> bool:
        """Valida si la URL del producto corresponde a la categoría esperada."""
        if not self.config:
            return True  # Si no hay config, aceptar todo
        
        patrones = self.config.get('patron_url', [])
        if not patrones:
            return True  # Si no hay patrones, aceptar todo
        
        url_lower = url.lower()
        for patron in patrones:
            if patron.lower() in url_lower:
                return True
        
        return False

    def _extract_urls_alternative_search(self, soup: BeautifulSoup) -> List[str]:
        """Búsqueda alternativa para encontrar URLs de productos cuando el método normal falla."""
        urls: List[str] = []
        
        # Método 1: Buscar en scripts JSON embebidos
        for script in soup.find_all('script'):
            script_text = script.get_text()
            if 'product' in script_text.lower() and '/p/' in script_text:
                # Buscar patrones de URL en JSON/JavaScript
                import re
                found_urls = re.findall(r'["\']([^"\']*?/p/[^"\']*?)["\']', script_text)
                for url in found_urls:
                    if self._is_valid_category_url(url):
                        full_url = urljoin(self.base_url, url)
                        urls.append(self._strip_tracking(full_url))
                        print(f"URL encontrada en script: {url[:60]}...")
        
        # Método 2: Buscar atributos data-* que contengan URLs
        for elem in soup.find_all(attrs={"data-href": True}):
            href = elem.get("data-href")
            if href and "/p/" in href and self._is_valid_category_url(href):
                full_url = urljoin(self.base_url, href)
                urls.append(self._strip_tracking(full_url))
                print(f"URL encontrada en data-href: {href[:60]}...")
        
        # Método 3: Buscar enlaces ocultos o con otros atributos
        for elem in soup.find_all(attrs={"href": True}):
            href = elem.get("href")
            if href and "/p/" in href and self._is_valid_category_url(href):
                full_url = urljoin(self.base_url, href)
                urls.append(self._strip_tracking(full_url))
                print(f"URL encontrada como enlace alternativo: {href[:60]}...")
        
        return urls[:20]  # Limitar para evitar duplicados excesivos

    def _get_ejemplo_urls_for_category(self) -> List[str]:
        """Obtiene URLs de ejemplo conocidas para cada categoría."""
        # Primero intentar buscar dinámicamente
        urls_dinamicas = self._buscar_urls_dinamicas()
        if urls_dinamicas:
            return urls_dinamicas
            
        # Fallback: URLs de ejemplo estáticas (solo para televisores que sabemos que funcionan)
        ejemplos_por_categoria = {
            "televisores": [
                "https://www.alkosto.com/tv-lg-65-pulgadas-165-cm-65ua8050-4k-uhd-led-smart-tv-con/p/8806096330241",
                "https://www.alkosto.com/tv-kalley-60-pulgadas-1524-cm-60g300-4k-uhd-led-smart-tv/p/7705946480048", 
                "https://www.alkosto.com/tv-tcl-55-pulgadas-139-cm-55v6c-4k-uhd-smart-tv-google/p/6921732899387",
                "https://www.alkosto.com/tv-samsung-55-pulgadas-1397-cm-u8000f-4k-uhd-led-crystal/p/8806097027584",
                "https://www.alkosto.com/tv-challenger-40-pulgadas-101-cm-40kg84-fhd-led-smart-tv/p/7705191044835"
            ]
        }
        
        urls = ejemplos_por_categoria.get(self.categoria, [])
        
        # Para televisores usar URLs estáticas confiables, para otras categorías usar búsqueda dinámica
        if self.categoria == "televisores" and urls:
            print(f"    ✅ Usando {len(urls)} URLs estáticas para {self.categoria}")
            return urls
        else:
            print(f"    🔍 Para {self.categoria}: usando solo búsqueda dinámica")
            return []

    def _buscar_urls_dinamicas(self) -> List[str]:
        """Intenta buscar URLs reales usando la función de búsqueda de Alkosto."""
        try:
            # Usar términos de búsqueda específicos por categoría
            terminos_busqueda = {
                "televisores": "tv smart",
                "celulares": "samsung galaxy",
                "domotica": "camara seguridad",
                "audifonos": "audifonos inalambricos",
                "cocina": "horno microondas",
                "lavado": "lavadora kg",
                "refrigeracion": "nevera litros",
                "videojuegos": "playstation xbox",
                "deportes": "bicicleta fitness"
            }
            
            termino = terminos_busqueda.get(self.categoria, self.categoria)
            print(f"Buscando productos con término: '{termino}'...")
            
            # Múltiples estrategias de búsqueda
            urls = []
            
            # Estrategia 1: Búsqueda estándar
            search_urls = [
                f"https://www.alkosto.com/search?text={termino.replace(' ', '%20')}",
                f"https://www.alkosto.com/search/?text={termino.replace(' ', '+')}",
                f"https://www.alkosto.com/{self.categoria}"  # URL directa de categoría
            ]
            
            for search_url in search_urls:
                try:
                    print(f"      Probando: {search_url}")
                    html_doc = self._get_html(search_url)
                    soup = BeautifulSoup(html_doc, "lxml")
                    
                    # Buscar enlaces con /p/
                    for a in soup.select('a[href*="/p/"]'):
                        href = a.get("href")
                        if href and "/p/" in href:
                            full_url = urljoin("https://www.alkosto.com", href)
                            clean_url = self._strip_tracking(full_url)
                            
                            if self._is_valid_category_url(clean_url):
                                urls.append(clean_url)
                                print(f"Encontrado: {clean_url[:60]}...")
                                
                            if len(urls) >= 5:  # Suficientes para la búsqueda
                                break
                    
                    if len(urls) >= 3:  # Si ya tenemos suficientes, parar
                        break
                        
                except Exception as e:
                    print(f"Error con {search_url}: {str(e)[:30]}...")
                    continue
            
            if urls:
                print(f"    ✅ Búsqueda estática encontró {len(urls)} URLs válidas")
                return urls[:5]
            else:
                print(f"Búsqueda estática no encontró URLs, intentando con Selenium...")
                return self._buscar_urls_con_selenium(termino)
            
        except Exception as e:
            print(f"Error en búsqueda dinámica: {str(e)[:50]}...")
            return []

    def _buscar_urls_con_selenium(self, termino: str) -> List[str]:
        """Busca URLs usando Selenium para contenido dinámico."""
        if not self.selenium_enabled:
            print(f"Selenium no disponible para búsqueda dinámica")
            return []
            
        try:
            # URLs a probar con Selenium
            search_urls = [
                self.base_url,  # URL de la categoría principal
                f"https://www.alkosto.com/search?text={termino.replace(' ', '%20')}"
            ]
            
            urls = []
            for search_url in search_urls:
                try:
                    print(f"Probando con Selenium: {search_url}")
                    html_doc = self._get_html_selenium(search_url)
                    soup = BeautifulSoup(html_doc, "lxml")
                    
                    # Buscar enlaces con /p/
                    product_links = soup.select('a[href*="/p/"]')
                    print(f"Encontrados {len(product_links)} enlaces con /p/")
                    
                    for a in product_links:
                        href = a.get("href")
                        if href and "/p/" in href:
                            full_url = urljoin("https://www.alkosto.com", href)
                            clean_url = self._strip_tracking(full_url)
                            
                            if self._is_valid_category_url(clean_url):
                                urls.append(clean_url)
                                print(f"Válido: {clean_url[:60]}...")
                            else:
                                print(f"No válido: {clean_url[:60]}...")
                                
                            if len(urls) >= 5:  # Suficientes para la búsqueda
                                break
                    
                    if len(urls) >= 3:  # Si ya tenemos suficientes, parar
                        break
                        
                except Exception as e:
                    print(f"Error con Selenium en {search_url}: {str(e)[:30]}...")
                    continue
            
            if urls:
                print(f"Selenium encontró {len(urls)} URLs válidas")
                return urls[:5]
            else:
                print(f"Selenium no encontró URLs válidas")
                return []
                
        except Exception as e:
            print(f"Error en búsqueda con Selenium: {str(e)[:50]}...")
            return []
        finally:
            # Cerrar Selenium después de usarlo
            self._close_selenium()

    def _generar_urls_busqueda(self, termino: str) -> List[str]:
        """Genera URLs usando búsqueda en tiempo real."""
        print(f"Generando URLs de búsqueda para: {termino}")
        return []  # Placeholder - se procesará dinámicamente



    def get_product_urls_with_load_more(self, max_productos: int = 20) -> List[str]:
        """Obtiene URLs de producto de la categoría actual.
        Intenta `?page=` y si no hay resultados, `?p=` como fallback.
        """
        max_productos = max(1, int(max_productos or 1))

        urls: List[str] = []
        page = 1
        # Intento 1: `?page=`
        while len(urls) < max_productos and page <= 10:
            url = self._build_paged_url(self.base_url, page, param="page")
            try:
                html_doc = self._get_html(url)
            except Exception:
                break
            soup = BeautifulSoup(html_doc, "lxml")
            batch = self._extract_listing_urls(soup)
            if not batch:
                break
            for u in batch:
                if len(urls) >= max_productos:
                    break
                urls.append(u)
            page += 1

        # Intento 2: `?p=` si el primero no dio nada
        if not urls:
            page = 1
            while len(urls) < max_productos and page <= 10:
                url = self._build_paged_url(self.base_url, page, param="p")
                try:
                    html_doc = self._get_html(url)
                except Exception:
                    break
                soup = BeautifulSoup(html_doc, "lxml")
                batch = self._extract_listing_urls(soup)
                if not batch:
                    break
                for u in batch:
                    if len(urls) >= max_productos:
                        break
                    urls.append(u)
                page += 1

        # Intento 3: URLs de ejemplo conocidas para testing (solo si no encontramos nada)
        if not urls:
            print(f"Buscando URLs de ejemplo para {self.categoria}...")
            ejemplo_urls = self._get_ejemplo_urls_for_category()
            for url in ejemplo_urls[:max_productos]:
                urls.append(url)

        return urls[:max_productos]

    # ------------------------
    # Parsing de producto
    # ------------------------
    def _text(self, el) -> str:
        if not el:
            return ""
        return html.unescape(" ".join(el.get_text(" ").split()).strip())

    def _get_title(self, soup: BeautifulSoup) -> str:
        # 1) itemprop=name
        el = soup.select_one('[itemprop="name"], meta[itemprop="name"][content]')
        if el:
            if el.name == "meta":
                return el.get("content", "").strip()
            return self._text(el)
        # 2) h1
        h1 = soup.select_one("h1")
        if h1:
            return self._text(h1)
        # 3) og:title
        og = soup.select_one('meta[property="og:title"][content]')
        if og:
            return og.get("content", "").strip()
        # 4) title
        t = soup.select_one("title")
        return self._text(t)

    def _parse_price_from_text(self, s: str) -> int:
        s = s.replace("\xa0", " ")
        # Quita palabras comunes
        s = re.sub(r"(?i)(precio|antes|ahora|oferta|ahorra|tarjeta|efectivo|con|desde)", " ", s)
        
        # Buscar patrones de precio colombiano específicos
        # Formato: $1.299.900, $2,499,900, $3999900, etc.
        price_patterns = [
            r'\$[\d,\.]+',  # $1.299.900 o $1,299,900
            r'[\d,\.]{4,}',  # 1299900 o 1.299.900
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, s)
            if matches:
                # Tomar el primer match válido
                for match in matches:
                    # Limpiar el match
                    clean_match = re.sub(r'[^\d]', '', match)
                    if clean_match and len(clean_match) >= 4:  # Al menos 4 dígitos
                        try:
                            price = int(clean_match)
                            # Validar que sea un precio razonable (entre 10,000 y 50,000,000 COP)
                            if 10000 <= price <= 50000000:
                                return price
                        except ValueError:
                            continue
        
        # Fallback: buscar números grandes
        nums = re.findall(r'\d{4,}', s)  # Al menos 4 dígitos
        if nums:
            for num in nums:
                try:
                    price = int(num)
                    if 10000 <= price <= 50000000:  # Precio razonable
                        return price
                except ValueError:
                    continue
        
        return 0

    def _get_price(self, soup: BeautifulSoup) -> int:
        # Intentos comunes
        candidates = [
            soup.select_one('[itemprop="price"]'),
            soup.select_one("[data-price], [data-product-price]"),
            soup.select_one(".price, .product-price, .product__price"),
            soup.select_one('meta[itemprop="price"][content]'),
        ]
        for el in candidates:
            if not el:
                continue
            if el.name == "meta":
                val = el.get("content")
                if val and val.strip():
                    try:
                        return int(float(val))
                    except Exception:
                        pass
            text = el.get("data-price") or el.get("data-product-price") or self._text(el)
            price = self._parse_price_from_text(text)
            if price > 0:
                return price

        # Búsqueda amplia por clases 'price'
        for el in soup.select("[class*='price']"):
            price = self._parse_price_from_text(self._text(el))
            if price > 0:
                return price
        return 0

    def _get_image(self, soup: BeautifulSoup) -> str:
        # og:image suele estar
        og = soup.select_one('meta[property="og:image"][content]')
        if og:
            return og.get("content", "").strip()
        # fallback a cualquier <img> grande
        for sel in [
            "[itemprop='image']",
            "#product-gallery img, .product-gallery img",
            "img",
        ]:
            img = soup.select_one(sel)
            if img and img.get("src"):
                return img.get("src").strip()
        return ""

    def _extract_specs_pairs(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Intenta armar pares clave:valor de las especificaciones.
        Busca tablas, listas con dt/dd o li strong + texto.
        """
        specs: Dict[str, str] = {}

        # 1) Tablas
        for table in soup.select("table"):
            # Sólo si parece de specs
            if not any(x in self._text(table).lower() for x in ["marca", "modelo", "sku", "ean", "garant", "color", "dimens", "peso"]):
                continue
            for row in table.select("tr"):
                tds = row.find_all(["td", "th"])
                if len(tds) >= 2:
                    key = self._text(tds[0])
                    val = self._text(tds[1])
                    if key and val:
                        specs[key] = val

        # 2) dl/dt/dd
        for dl in soup.select("dl"):
            dts = dl.find_all("dt")
            dds = dl.find_all("dd")
            if len(dts) == 0 or len(dts) != len(dds):
                continue
            for dt, dd in zip(dts, dds):
                key = self._text(dt)
                val = self._text(dd)
                if key and val:
                    specs[key] = val

        # 3) listas tipo li > strong: valor
        for li in soup.select("li"):
            strong = li.find("strong")
            if strong:
                key = self._text(strong)
                val = self._text(li).replace(key, "").strip(" :\n\t-—•")
                if key and val:
                    specs[key] = val
        return specs

    def _guess_brand(self, title: str, specs: Dict[str, str]) -> str:
        # 1) De specs comunes
        for k in ["Marca", "MARCA", "brand", "Fabricante"]:
            if k in specs and specs[k].strip():
                return specs[k].strip()
        # 2) Heurística del título: primera palabra destacada
        # Evita capturar palabras genéricas
        tokens = re.split(r"\s+|,|\|", title)
        for tok in tokens:
            t = tok.strip().strip("-–—:·•|,.")
            if 2 <= len(t) <= 20 and t.lower() not in {"tv", "smart", "led", "qled", "uhd", "4k", "full", "hd", "inch", "pulgadas", "lcd", "neo", "ultra"}:
                # Empieza en mayúscula
                if re.match(r"^[A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑ0-9\-]+$", t):
                    return t
        return ""

    def _extract_size_inches(self, title: str, specs: Dict[str, str]) -> Optional[str]:
        # TVs: 32", 55", 65 pulgadas, etc.
        patterns = [
            r"(\d{2,3})\s*\"",  # 55"
            r"(\d{2,3})\s*(?:pulg|pulgadas)",
        ]
        for pat in patterns:
            m = re.search(pat, title, flags=re.IGNORECASE)
            if m:
                return f"{m.group(1)}\""
        for k in ["Tamaño", "Tamano", "Tamaño de pantalla", "Tamaño pantalla", "Pantalla"]:
            if k in specs:
                for pat in patterns:
                    m = re.search(pat, specs[k], flags=re.IGNORECASE)
                    if m:
                        return f"{m.group(1)}\""
        return None

    def _get_breadcrumb_category(self, soup: BeautifulSoup) -> Optional[str]:
        crumbs = [self._text(a) for a in soup.select("nav a, .breadcrumb a, [itemprop='itemListElement'] a")]
        if crumbs:
            # última miga suele ser el producto, penúltima la categoría
            if len(crumbs) >= 2:
                return crumbs[-2]
        return None

    def _rating(self, soup: BeautifulSoup) -> Tuple[Optional[float], Optional[int]]:
        # ratingValue y reviewCount si existen
        rv = soup.select_one('[itemprop="ratingValue"], meta[itemprop="ratingValue"][content]')
        rc = soup.select_one('[itemprop="reviewCount"], meta[itemprop="reviewCount"][content]')
        rating: Optional[float] = None
        count: Optional[int] = None
        if rv:
            val = rv.get("content") if rv.name == "meta" else self._text(rv)
            try:
                rating = float(val.replace(",", "."))
            except Exception:
                pass
        if rc:
            val = rc.get("content") if rc.name == "meta" else self._text(rc)
            try:
                count = int(re.sub(r"\D", "", val))
            except Exception:
                pass
        return rating, count

    def scrape_product(self, url: str):
        html_doc = self._get_html(url)
        soup = BeautifulSoup(html_doc, "lxml")

        title = self._get_title(soup)
        price = self._get_price(soup)
        image = self._get_image(soup)
        specs = self._extract_specs_pairs(soup)
        brand = self._guess_brand(title, specs)
        size = self._extract_size_inches(title, specs)
        breadcrumb_cat = self._get_breadcrumb_category(soup)
        rating_val, rating_count = self._rating(soup)

        # Extras comunes
        extras: Dict[str, object] = {}
        for key in [
            "Modelo", "modelo", "SKU", "Sku", "sku",
            "EAN", "ean", "UPC", "upc",
            "Garantía", "Garantia", "garantía", "garantia",
            "Color", "color",
            "Dimensiones", "dimensiones", "Peso", "peso",
            "Material", "material",
            "Contenido de la caja", "Contenido de la Caja", "Contenido",
            "Voltaje", "voltaje",
        ]:
            if key in specs and specs[key]:
                extras[key] = specs[key]

        # Disponibilidad (heurística)
        stock_text = "".join(
            [self._text(el) for el in soup.select(".availability, .stock, .product-inventory, .product-availability")]
        ).lower()
        if stock_text:
            extras["disponibilidad"] = (
                "en stock" if any(s in stock_text for s in ["en stock", "disponible"]) else stock_text
            )

        if rating_count is not None:
            extras["ratings_count"] = rating_count

        if specs:
            extras["specs_norm"] = specs  # specs crudos normalizados clave:valor

        # Construcción del objeto ProductoGenerico con los ATRIBUTOS ACTUALES
        payload = {
            "nombre": title,
            "precio": int(price) if isinstance(price, (int, float)) else 0,
            "marca": brand,
            "tamaño": size,  # mantener con tilde porque así lo consumen
            "calificacion": rating_val,
            "imagen": image,
            "url_producto": self._strip_tracking(url),
            "fuente": "alkosto",
            "categoria": breadcrumb_cat or self.categoria,
            "timestamp_extraccion": datetime.now(),
            "extraction_status": "ok" if title else "sin_titulo",
            "contador_extraccion": 1,
            "atributos_extra": extras,
        }

        # Instanciar entidades del dominio
        if self.modo_generico:
            if ProductoGenerico is None:
                # Fallback mínimo si la clase no está importable
                return payload
            try:
                return ProductoGenerico(**payload)  # type: ignore
            except TypeError:
                # Por si tu clase tiene un from_dict
                if hasattr(ProductoGenerico, "from_dict"):
                    return ProductoGenerico.from_dict(payload)  # type: ignore
                return payload
        else:
            # Compatibilidad: crear Televisor sólo si la categoría es TV
            # Mapeo simple genérico -> Televisor (ajusta si tu constructor difiere)
            if Televisor is None:
                return payload
            if self.categoria != "televisores":
                return payload

            # Heurística de pulgadas para Televisor
            pulgadas = None
            if size:
                m = re.search(r"(\d{2,3})", size)
                if m:
                    try:
                        pulgadas = int(m.group(1))
                    except Exception:
                        pass

            try:
                return Televisor(
                    nombre=title,
                    precio=int(price),
                    marca=brand,
                    tamano_pulgadas=pulgadas,
                    imagen=image,
                    url_producto=self._strip_tracking(url),
                    fuente="alkosto",
                    calificacion=rating_val,
                    categoria=breadcrumb_cat or self.categoria,
                    timestamp_extraccion=datetime.now(),
                    extraction_status="ok" if title else "sin_titulo",
                    contador_extraccion=1,
                    atributos_extra=extras,
                )
            except TypeError:
                # Si tu Televisor usa otro orden o nombres, ajusta aquí
                return payload


# Fin del archivo
