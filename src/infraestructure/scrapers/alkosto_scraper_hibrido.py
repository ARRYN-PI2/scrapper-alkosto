import re
from typing import List, Optional, Union
from bs4 import BeautifulSoup
from loguru import logger
from urllib.parse import urljoin, urlparse
import requests
import time

from src.infraestructure.scrapers.base_scraper import BaseScraper
from src.domain.entities.televisor import Televisor
from src.domain.entities.producto_generico import ProductoGenerico, get_categoria_config


class AlkostoScraperHibrido(BaseScraper):
    """
    Scraper híbrido expandido para TODAS las categorías de Alkosto.
    
    COMPATIBILIDAD: 100% compatible con código existente de televisores.
    NUEVAS CAPACIDADES: Soporte para 9 categorías de productos.
    """
    
    def __init__(self, categoria: str = "televisores", modo_generico: bool = False, delay_between_requests: float = 2.0, max_retries: int = 3):
        """
        Inicializa el scraper híbrido expandido.
        
        Args:
            categoria: Categoría a scrapear (televisores, celulares, domotica, etc.)
            modo_generico: True para ProductoGenerico, False para Televisor
            delay_between_requests: Segundos de pausa entre peticiones
            max_retries: Número máximo de reintentos
        """
        super().__init__(delay_between_requests, max_retries)
        
        self.categoria = categoria.lower()
        self.modo_generico = modo_generico
        self.categoria_config = get_categoria_config(self.categoria)
        
        # URLs por categoría
        if self.categoria_config:
            self.base_url = "https://www.alkosto.com"
            self.category_url = self.categoria_config["url"]
            self.max_productos_esperados = self.categoria_config["max_productos_esperados"]
            logger.info(f"🎯 Configurado para categoría: {self.categoria} - Genérico: {self.modo_generico}")
            logger.info(f"📊 Productos esperados: ~{self.max_productos_esperados}")
        else:
            # Fallback a televisores (compatibilidad total)
            self.base_url = "https://www.alkosto.com"
            self.category_url = "https://www.alkosto.com/tv/smart-tv/c/BI_120_ALKOS"
            self.max_productos_esperados = 200
            logger.warning(f"⚠️ Categoría '{self.categoria}' no encontrada, usando televisores")
    
    def get_product_urls_with_load_more(self, max_productos: int = None) -> List[str]:
        """
        MÉTODO PRINCIPAL: Obtiene TODAS las URLs usando carga dinámica.
        Adaptado para cualquier categoría usando requests (como tu código que funciona).
        """
        if max_productos is None:
            max_productos = self.max_productos_esperados
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.alkosto.com',
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        all_product_urls = []
        current_url = self.category_url
        
        logger.info(f"🚀 Iniciando scraping de {self.categoria} (máximo {max_productos} productos)")
        
        # Usar el mismo patrón que tu código que funciona
        max_pages = 20  # Límite de seguridad
        
        for page in range(1, max_pages + 1):
            try:
                logger.info(f"📄 Navegando a página {page}: {current_url}")
                
                response = session.get(current_url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar enlaces de productos
                page_products = []
                product_links = soup.find_all('a', href=True)
                
                for link in product_links:
                    href = link.get('href')
                    if href and self._is_product_url(href):
                        clean_href = href.split('?')[0]
                        full_url = urljoin(self.base_url, clean_href)
                        if full_url not in all_product_urls:
                            all_product_urls.append(full_url)
                            page_products.append(full_url)
                
                logger.info(f"✅ Página {page}: {len(page_products)} productos nuevos. Total: {len(all_product_urls)}")
                
                if len(page_products) == 0:
                    logger.info(f"🏁 No se encontraron productos en página {page}. Terminando.")
                    break
                
                # Buscar progreso en la página
                page_text = soup.get_text()
                if self._check_completion_indicators(page_text, len(all_product_urls)):
                    break
                
                # Construir URL de siguiente página
                current_url = f"{self.category_url}?page={page}&sort=relevance"
                
                # Si ya tenemos suficientes productos, terminar
                if len(all_product_urls) >= max_productos:
                    logger.info(f"🎉 ¡Objetivo alcanzado! {len(all_product_urls)} productos obtenidos")
                    break
                
                time.sleep(self.delay_between_requests)
                
            except Exception as e:
                logger.error(f"❌ Error en página {page}: {e}")
                break
        
        logger.info(f"🎉 Scraping de {self.categoria} completado: {len(all_product_urls)} URLs obtenidas")
        return all_product_urls[:max_productos]  # Recortar al máximo solicitado
    
    def _check_completion_indicators(self, page_text: str, current_count: int) -> bool:
        """
        Verifica indicadores de que ya se cargaron todos los productos.
        """
        try:
            # Buscar patrón "X de Y productos"
            match = re.search(r'(\d+)\s+de\s+(\d+)\s+productos', page_text)
            if match:
                current_shown = int(match.group(1))
                total_available = int(match.group(2))
                logger.info(f"📊 Progreso detectado: {current_shown} de {total_available} productos")
                
                if current_shown >= total_available:
                    logger.info(f"🎉 ¡Todos los productos cargados! {total_available} total")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando indicadores: {e}")
            return False
    
    def _is_product_url(self, url: str) -> bool:
        """
        Determina si una URL corresponde a un producto de la categoría actual.
        """
        if not url or '/p/' not in url:
            return False
        
        if not self.categoria_config:
            # Fallback para televisores
            return url.startswith('/tv-') and '/p/' in url
        
        # Usar patrones específicos de la categoría
        patterns = self.categoria_config.get("patron_url", [])
        url_lower = url.lower()
        
        return any(pattern in url_lower for pattern in patterns)
    
    def scrape_product(self, product_url: str) -> Union[Televisor, ProductoGenerico]:
        """
        Extrae información de un producto.
        EXPANDIDO: Maneja todos los atributos de tu lista + específicos por categoría.
        """
        response = self.make_request(product_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraer TODOS los atributos de tu lista
        nombre = self._extract_name(soup)
        precio = self._extract_price(soup)
        marca = self._extract_brand(soup)
        calificacion = self._extract_rating(soup)
        imagen = self._extract_image(soup)
        tamaño = self._extract_size(soup)
        
        if self.modo_generico:
            # Crear ProductoGenerico con TODOS tus atributos
            producto = ProductoGenerico(
                nombre=nombre,
                precio=precio,
                marca=marca,
                categoria=self.categoria,
                url_producto=product_url,
                fuente="alkosto",
                calificacion=calificacion,
                tamaño=tamaño,
                imagen=imagen
                # timestamp_extraccion, extraction_status, contador_extraccion se asignan automáticamente
            )
            
            # Agregar atributos específicos por categoría si la categoría es televisores
            if self.categoria == "televisores":
                resolucion = self._extract_resolution(soup)
                tamano_pulgadas = self._extract_screen_size_number(soup)
                producto.agregar_atributo_extra('resolucion', resolucion)
                producto.agregar_atributo_extra('tamano_pulgadas', tamano_pulgadas)
            
            return producto
            
        else:
            # Modo compatibilidad: crear Televisor (solo para televisores)
            if self.categoria == "televisores":
                tamano_pulgadas = self._extract_screen_size_number(soup)
                resolucion = self._extract_resolution(soup)
                
                return Televisor(
                    nombre=nombre,
                    precio=precio,
                    tamano_pulgadas=tamano_pulgadas,
                    calificacion=calificacion,
                    marca=marca,
                    resolucion=resolucion,
                    pagina_fuente="alkosto",
                    url_producto=product_url
                )
            else:
                # Para otras categorías en modo no genérico, usar genérico automáticamente
                logger.warning(f"Categoría {self.categoria} requiere modo genérico. Cambiando automáticamente.")
                self.modo_generico = True
                return self.scrape_product(product_url)
    
    # === MÉTODOS DE EXTRACCIÓN UNIVERSALES (tu lista de atributos) ===
    
    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extrae el nombre del producto."""
        try:
            name_element = soup.find('h1')
            if name_element:
                return name_element.get_text(strip=True)
            
            title_element = soup.find('title')
            if title_element:
                title_text = title_element.get_text(strip=True)
                if '|' in title_text:
                    title_text = title_text.split('|')[0].strip()
                return title_text
            
            logger.warning("No se pudo extraer el nombre del producto")
            return "Nombre no disponible"
            
        except Exception as e:
            logger.error(f"Error extrayendo nombre: {e}")
            return "Nombre no disponible"
    
    def _extract_price(self, soup: BeautifulSoup) -> float:
        """Extrae el precio del producto."""
        try:
            # Selectores comunes de precio en Alkosto
            price_selectors = [
                '#js-original_price',
                'span.before-price__basePrice',
                '.price-current',
                '.price-now'
            ]
            
            for selector in price_selectors:
                price_element = soup.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    price_numbers = re.findall(r'[\d.]+', price_text.replace(',', '').replace('$', ''))
                    if price_numbers:
                        return float(price_numbers[0].replace('.', ''))
            
            logger.warning("No se pudo extraer el precio")
            return 0.0
            
        except Exception as e:
            logger.error(f"Error extrayendo precio: {e}")
            return 0.0
    
    def _extract_brand(self, soup: BeautifulSoup) -> str:
        """Extrae la marca del producto."""
        try:
            # Buscar elemento específico de marca
            brand_element = soup.select_one('div.product__item__information__brand')
            if brand_element:
                return brand_element.get_text(strip=True)
            
            # Buscar en el título
            title_element = soup.find('h1')
            if title_element:
                title_text = title_element.get_text().upper()
                
                # Lista expandida de marcas (todas las categorías)
                all_brands = [
                    # Televisores
                    'SAMSUNG', 'PANASONIC', 'HISENSE', 'CHALLENGER', 'PHILIPS', 
                    'SKYWORTH', 'TOSHIBA', 'KALLEY', 'VITRON', 'XIAOMI', 
                    'HUAWEI', 'SHARP', 'HAIER', 'COOCAA', 'SANKEY',
                    'SONY', 'ASUS', 'TCL', 'AOC', 'RCA', 'LG',
                    # Celulares
                    'APPLE', 'MOTOROLA', 'HONOR', 'REALME', 'OPPO', 'VIVO',
                    'REDMI', 'ONEPLUS', 'NOKIA',
                    # Electrodomésticos
                    'WHIRLPOOL', 'ELECTROLUX', 'MABE', 'HACEB', 'FRIGIDAIRE',
                    'BOSCH', 'SIEMENS',
                    # Audio
                    'JBL', 'BEATS', 'BOSE', 'SENNHEISER', 'SKULLCANDY',
                    # Gaming
                    'MICROSOFT', 'NINTENDO', 'RAZER', 'LOGITECH'
                ]
                
                # Buscar marca en palabras completas
                words = title_text.split()
                for brand in all_brands:
                    if brand in words:
                        return brand.capitalize()
                
                # Buscar como substring (excluyendo casos problemáticos)
                for brand in all_brands:
                    if brand in title_text and brand not in ['LG']:
                        return brand.capitalize()
                
                # Caso especial para LG
                if ' LG ' in title_text or title_text.startswith('LG '):
                    return 'Lg'
                
                # Extraer primera palabra si no es genérica
                if len(words) > 1 and words[0] not in ['TV', 'SMART', 'TELEVISOR', 'CELULAR']:
                    return words[0].capitalize()
            
            logger.warning("No se pudo extraer la marca")
            return "Desconocida"
            
        except Exception as e:
            logger.error(f"Error extrayendo marca: {e}")
            return "Desconocida"
    
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extrae la calificación del producto."""
        try:
            rating_selectors = [
                'span.averageNumber',
                '.rating-value',
                '.star-rating'
            ]
            
            for selector in rating_selectors:
                rating_element = soup.select_one(selector)
                if rating_element:
                    rating_text = rating_element.get_text(strip=True)
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        return float(rating_match.group(1))
            
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo calificación: {e}")
            return None
    
    def _extract_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae la URL de la imagen principal."""
        try:
            # Selectores para imágenes de producto
            img_selectors = [
                'img.product-image',
                'img[data-src*="product"]',
                '.product-gallery img',
                '.main-image img',
                'img[alt*="producto"]'
            ]
            
            for selector in img_selectors:
                img = soup.select_one(selector)
                if img:
                    src = img.get('src') or img.get('data-src')
                    if src:
                        return self._normalize_image_url(src)
            
            # Fallback: buscar cualquier imagen grande
            all_imgs = soup.find_all('img')
            for img in all_imgs:
                src = img.get('src') or img.get('data-src')
                if src and ('product' in src.lower() or '300x300' in src):
                    return self._normalize_image_url(src)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo imagen: {e}")
            return None
    
    def _normalize_image_url(self, url: str) -> str:
        """Normaliza una URL de imagen."""
        if url.startswith('//'):
            return 'https:' + url
        elif url.startswith('/'):
            return 'https://www.alkosto.com' + url
        else:
            return url
    
    def _extract_size(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrae el tamaño/dimensiones del producto."""
        try:
            # Para televisores, buscar pulgadas
            if self.categoria == "televisores":
                size_elements = soup.find_all('div', class_='new-container__table__classifications___type__item_result')
                for element in size_elements:
                    text = element.get_text(strip=True)
                    if 'pulgadas' in text.lower():
                        size_match = re.search(r'(\d+)\s*pulgadas', text.lower())
                        if size_match:
                            return f"{size_match.group(1)} pulgadas"
                
                # Buscar en título
                title_element = soup.find('h1')
                if title_element:
                    title_text = title_element.get_text()
                    size_match = re.search(r'(\d+)["\']|(\d+)\s*pulgadas', title_text)
                    if size_match:
                        size_num = size_match.group(1) or size_match.group(2)
                        return f"{size_num} pulgadas"
            
            # Para otras categorías, buscar patrones generales
            size_patterns = [
                r'(\d+\.?\d*)\s*(gb|tb)',  # Almacenamiento
                r'(\d+\.?\d*)\s*(kg)',     # Peso
                r'(\d+\.?\d*)\s*(litros)', # Capacidad
                r'(\d+)\s*(puestos)'       # Puestos cocina
            ]
            
            all_text = soup.get_text()
            for pattern in size_patterns:
                match = re.search(pattern, all_text.lower())
                if match:
                    return f"{match.group(1)} {match.group(2)}"
            
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo tamaño: {e}")
            return None
    
    # === MÉTODOS DE COMPATIBILIDAD PARA TELEVISORES ===
    
    def _extract_screen_size_number(self, soup: BeautifulSoup) -> int:
        """Extrae tamaño de pantalla como número (compatibilidad con Televisor)."""
        try:
            size_elements = soup.find_all('div', class_='new-container__table__classifications___type__item_result')
            for element in size_elements:
                text = element.get_text(strip=True)
                if 'pulgadas' in text.lower():
                    size_match = re.search(r'(\d+)\s*pulgadas', text.lower())
                    if size_match:
                        return int(size_match.group(1))
            
            title_element = soup.find('h1')
            if title_element:
                title_text = title_element.get_text()
                size_match = re.search(r'(\d+)["\']|(\d+)\s*pulgadas', title_text)
                if size_match:
                    return int(size_match.group(1) or size_match.group(2))
            
            return 0
        except Exception as e:
            logger.error(f"Error extrayendo tamaño numérico: {e}")
            return 0
    
    def _extract_resolution(self, soup: BeautifulSoup) -> str:
        """Extrae la resolución (específico para TVs)."""
        try:
            spec_elements = soup.find_all('div', class_='new-container__table__classifications___type__item_result')
            for element in spec_elements:
                text = element.get_text(strip=True).upper()
                if '4K' in text or 'UHD' in text:
                    return '4K'
                elif 'FHD' in text or 'FULL HD' in text:
                    return 'Full HD'
                elif 'HD' in text:
                    return 'HD'
            
            title_element = soup.find('h1')
            if title_element:
                title_text = title_element.get_text().upper()
                if '8K' in title_text:
                    return '8K'
                elif '4K' in title_text or 'UHD' in title_text:
                    return '4K'
                elif 'FULL HD' in title_text or 'FHD' in title_text:
                    return 'Full HD'
                elif 'HD' in title_text:
                    return 'HD'
            
            return 'HD'
        except Exception as e:
            logger.error(f"Error extrayendo resolución: {e}")
            return 'HD'