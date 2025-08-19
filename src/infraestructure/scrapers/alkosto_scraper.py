import re
from typing import List, Optional
from bs4 import BeautifulSoup
from loguru import logger
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

from src.infraestructure.scrapers.base_scraper import BaseScraper
from src.domain.entities.televisor import Televisor


class AlkostoScraper(BaseScraper):
    """
    Scraper específico para Alkosto.
    
    Implementa la lógica específica para extraer datos de televisores
    desde el sitio web de Alkosto.
    """
    
    def __init__(self, delay_between_requests: float = 2.0, max_retries: int = 3):
        super().__init__(delay_between_requests, max_retries)
        self.base_url = "https://www.alkosto.com"
        self.tv_category_url = "https://www.alkosto.com/tv/smart-tv/c/BI_120_ALKOS"
    
    def get_product_urls(self, max_pages: int = 1) -> List[str]:
        """
        Obtiene todas las URLs de productos de televisores de Alkosto usando Selenium.
        MÉTODO ORIGINAL - USA PAGINACIÓN (limitado a primeros 25 productos)
        
        Args:
            max_pages: Número máximo de páginas a recorrer
            
        Returns:
            Lista de URLs de productos
        """
        product_urls = []
        
        # Configurar Chrome en modo headless (sin ventana)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Sin ventana visible
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Agregar user agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = None
        try:
            logger.info("🚀 Iniciando navegador Chrome...")
            # Usar ChromeDriverManager con el argumento service
            from selenium.webdriver.chrome.service import Service
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)  # Esperar hasta 10 segundos por elementos
            
            for page_num in range(1, max_pages + 1):
                try:
                    # URL de la página con paginación de Alkosto
                    if page_num == 1:
                        page_url = self.tv_category_url
                    else:
                        page_url = f"{self.tv_category_url}?page={page_num-1}"
                    
                    logger.info(f"🔍 Navegando a página {page_num}: {page_url}")
                    driver.get(page_url)
                    
                    # Esperar a que la página cargue completamente
                    logger.info("⏳ Esperando que los productos se carguen...")
                    time.sleep(5)  # Dar tiempo para que JavaScript cargue los productos
                    
                    # Buscar enlaces de productos usando Selenium
                    try:
                        # Esperar hasta que aparezcan enlaces de productos
                        WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/tv-'][href*='/p/']"))
                        )
                    except:
                        logger.warning(f"No se encontraron productos en página {page_num} después de esperar")
                    
                    # Obtener el HTML ya renderizado por JavaScript
                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    
                    # Buscar todos los enlaces que parezcan productos de TV
                    product_links = soup.find_all('a', href=True)
                    
                    page_products = []
                    for link in product_links:
                        href = link.get('href')
                        if href and self._is_product_url(href):
                            # Limpiar los parámetros de tracking
                            clean_href = href.split('?')[0]
                            full_url = urljoin(self.base_url, clean_href)
                            if full_url not in product_urls:  # Evitar duplicados
                                product_urls.append(full_url)
                                page_products.append(full_url)
                    
                    logger.info(f"✅ Encontrados {len(page_products)} productos en página {page_num}")
                    
                    # Si no hay productos en esta página, probablemente llegamos al final
                    if len(page_products) == 0:
                        logger.info(f"🏁 No se encontraron productos en página {page_num}. Terminando.")
                        break
                    
                    # Pausa entre páginas
                    if page_num < max_pages:
                        time.sleep(self.delay_between_requests)
                        
                except Exception as e:
                    logger.error(f"❌ Error scrapeando página {page_num}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"❌ Error configurando Selenium: {e}")
            logger.error("💡 Asegúrate de tener Chrome instalado y ChromeDriver en PATH")
            
        finally:
            # Cerrar el navegador
            if driver:
                driver.quit()
                logger.info("🔒 Navegador cerrado")
        
        logger.info(f"🎉 Total de URLs de productos encontradas: {len(product_urls)}")
        return product_urls

    def get_product_urls_with_load_more(self, max_products: int = 155) -> List[str]:
        """
        MÉTODO NUEVO - Obtiene TODOS los productos haciendo clic en "Mostrar más".
        
        Obtiene todas las URLs de productos de televisores de Alkosto usando Selenium.
        Hace clic en "Mostrar más" hasta cargar todos los productos.
        
        Args:
            max_products: Número máximo de productos a cargar (155 según Alkosto)
            
        Returns:
            Lista de URLs de productos
        """
        product_urls = []
        
        # Configurar Chrome en modo headless (sin ventana)
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Comentar para ver el navegador
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Agregar user agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = None
        try:
            logger.info("🚀 Iniciando navegador Chrome...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)
            
            # Navegar a la página inicial
            logger.info(f"🔍 Navegando a: {self.tv_category_url}")
            driver.get(self.tv_category_url)
            
            # Esperar a que la página cargue completamente
            logger.info("⏳ Esperando que los productos iniciales se carguen...")
            time.sleep(5)
            
            # Contador de intentos para evitar bucles infinitos
            max_attempts = 25  # Máximo de veces que intentará hacer clic en "mostrar más"
            #PAra los 158 que tiene alkosto funciona bien por ahora
            attempts = 0
            
            while len(product_urls) < max_products and attempts < max_attempts:
                attempts += 1
                
                # Obtener productos actuales en la página
                current_products = self._extract_current_products(driver)
                
                # Agregar nuevos productos únicos a la lista
                new_products_count = 0
                for product_url in current_products:
                    if product_url not in product_urls:
                        product_urls.append(product_url)
                        new_products_count += 1
                
                logger.info(f"📦 Productos encontrados: {len(product_urls)} (nuevos: {new_products_count})")
                
                # Si ya tenemos suficientes productos, salir
                if len(product_urls) >= max_products:
                    logger.info(f"✅ Se alcanzó el objetivo de {max_products} productos")
                    break
                
                # Buscar y hacer clic en el botón "Mostrar más"
                show_more_button = self._find_show_more_button(driver)
                
                if show_more_button:
                    try:
                        # Verificar si el botón está habilitado
                        if not show_more_button.is_enabled():
                            logger.info("🏁 Botón 'Mostrar más' deshabilitado. No hay más productos.")
                            break
                        
                        # Scroll hasta el botón para asegurar que esté visible
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_more_button)
                        time.sleep(2)
                        
                        # Hacer clic en el botón usando JavaScript
                        logger.info(f"🔄 Haciendo clic en 'Mostrar más' (intento {attempts})")
                        driver.execute_script("arguments[0].click();", show_more_button)
                        
                        # Esperar a que aparezcan los nuevos productos
                        logger.info("⏳ Esperando que se carguen nuevos productos...")
                        time.sleep(7)
                        
                        # Verificar si realmente se cargaron más productos
                        new_current_products = self._extract_current_products(driver)
                        if len(new_current_products) <= len(current_products):
                            logger.warning("⚠️ No se detectaron productos nuevos. Esperando un poco más...")
                            time.sleep(5)
                            new_current_products = self._extract_current_products(driver)
                            if len(new_current_products) <= len(current_products):
                                logger.info("🏁 No se cargaron más productos después de esperar")
                                break
                        
                        logger.info(f"✅ Se cargaron {len(new_current_products) - len(current_products)} productos nuevos")
                        
                    except Exception as e:
                        logger.error(f"❌ Error haciendo clic en 'Mostrar más': {e}")
                        # Intentar una vez más con método alternativo
                        try:
                            logger.info("🔄 Intentando método alternativo de clic...")
                            show_more_button.click()
                            time.sleep(5)
                        except:
                            logger.error("❌ Método alternativo también falló")
                            break
                else:
                    logger.info("🏁 No se encontró botón 'Mostrar más'. Todos los productos ya están cargados.")
                    break
            
            # Log final
            if attempts >= max_attempts:
                logger.warning(f"⚠️ Se alcanzó el máximo de intentos ({max_attempts})")
            
        except Exception as e:
            logger.error(f"❌ Error configurando Selenium: {e}")
            logger.error("💡 Asegúrate de tener Chrome instalado y ChromeDriver en PATH")
            
        finally:
            # Cerrar el navegador
            if driver:
                driver.quit()
                logger.info("🔒 Navegador cerrado")
        
        logger.info(f"🎉 Total de URLs de productos encontradas: {len(product_urls)}")
        return product_urls

    def _extract_current_products(self, driver) -> List[str]:
        """
        Extrae todas las URLs de productos actualmente visibles en la página.
        
        Args:
            driver: WebDriver de Selenium
            
        Returns:
            Lista de URLs de productos únicos
        """
        try:
            # Obtener el HTML actual
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Buscar todos los enlaces que parezcan productos de TV
            product_links = soup.find_all('a', href=True)
            
            current_products = []
            for link in product_links:
                href = link.get('href')
                if href and self._is_product_url(href):
                    # Limpiar los parámetros de tracking
                    clean_href = href.split('?')[0]
                    full_url = urljoin(self.base_url, clean_href)
                    if full_url not in current_products:  # Evitar duplicados
                        current_products.append(full_url)
            
            return current_products
            
        except Exception as e:
            logger.error(f"Error extrayendo productos actuales: {e}")
            return []

    def _find_show_more_button(self, driver):
        """
        Encuentra el botón "Mostrar más" específico de Alkosto.
        
        Args:
            driver: WebDriver de Selenium
            
        Returns:
            WebElement del botón o None si no se encuentra
        """
        try:
            # Selector específico de Alkosto
            alkosto_selectors = [
                "button.ais-InfiniteHits-loadMore",
                "button.js-load-more", 
                ".ais-InfiniteHits-loadMore.button-primary",
                "button[class*='ais-InfiniteHits-loadMore']",
                ".product__listing__load-more"
            ]
            
            # Selectores de respaldo
            fallback_selectors = [
                "//button[contains(text(), 'Mostrar más productos')]",
                "//button[contains(text(), 'Mostrar más')]",
                "//button[contains(text(), 'Cargar más')]",
                "button[class*='load-more']",
                "button[class*='show-more']"
            ]
            
            # Combinar todos los selectores
            button_selectors = alkosto_selectors + fallback_selectors
            
            for selector in button_selectors:
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        elements = driver.find_elements(By.XPATH, selector)
                    else:
                        # CSS selector
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        # Verificar que el elemento sea visible y clickeable
                        if element.is_displayed() and element.is_enabled():
                            logger.info(f"✅ Botón 'Mostrar más' encontrado con selector: {selector}")
                            return element
                            
                except Exception:
                    continue
            
            logger.warning("⚠️ No se encontró botón 'Mostrar más'")
            return None
            
        except Exception as e:
            logger.error(f"Error buscando botón 'Mostrar más': {e}")
            return None
    
    def _is_product_url(self, url: str) -> bool:
        """
        Determina si una URL corresponde a un producto de televisor.
        
        Args:
            url: URL a verificar
            
        Returns:
            True si es URL de producto de TV
        """
        # Patrón específico para productos de TV en Alkosto
        # Formato: /tv-[marca]-[especificaciones]/p/[código]
        return (
            url.startswith('/tv-') and 
            '/p/' in url and 
            url.count('/') >= 3  # Al menos /tv-.../p/codigo
        )
    
    def scrape_product(self, product_url: str) -> Televisor:
        """
        Extrae la información de un producto específico de Alkosto.
        
        Args:
            product_url: URL del producto
            
        Returns:
            Objeto Televisor con los datos extraídos
        """
        response = self.make_request(product_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extraer datos del producto usando los selectores reales de Alkosto
        nombre = self._extract_name(soup)
        precio = self._extract_price(soup)
        tamano_pulgadas = self._extract_screen_size(soup)
        calificacion = self._extract_rating(soup)
        marca = self._extract_brand(soup)
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
    
    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extrae el nombre completo del producto."""
        try:
            # Buscar el título principal del producto (h1)
            name_element = soup.find('h1')
            if name_element:
                return name_element.get_text(strip=True)
            
            # Fallback: buscar en title
            title_element = soup.find('title')
            if title_element:
                title_text = title_element.get_text(strip=True)
                # Limpiar el título (quitar " | Alkosto" etc.)
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
            # Primero buscar precio actual (con descuento)
            current_price = soup.select_one('#js-original_price')
            if current_price:
                price_text = current_price.get_text(strip=True)
                # Extraer solo números del texto del precio
                price_numbers = re.findall(r'[\d.]+', price_text.replace(',', '').replace('$', ''))
                if price_numbers:
                    # Tomar el primer número encontrado (antes de "Hoy")
                    return float(price_numbers[0].replace('.', ''))
            
            # Si no hay precio con descuento, buscar precio base
            base_price = soup.select_one('span.before-price__basePrice')
            if base_price:
                price_text = base_price.get_text(strip=True)
                price_numbers = re.findall(r'[\d.]+', price_text.replace(',', '').replace('$', ''))
                if price_numbers:
                    return float(price_numbers[0].replace('.', ''))
            
            logger.warning("No se pudo extraer el precio")
            return 0.0
            
        except Exception as e:
            logger.error(f"Error extrayendo precio: {e}")
            return 0.0
    
    def _extract_screen_size(self, soup: BeautifulSoup) -> int:
        """Extrae el tamaño de pantalla en pulgadas."""
        try:
            # Buscar en las especificaciones usando el selector específico
            size_elements = soup.find_all('div', class_='new-container__table__classifications___type__item_result')
            for element in size_elements:
                text = element.get_text(strip=True)
                if 'pulgadas' in text.lower():
                    # Extraer número de pulgadas
                    size_match = re.search(r'(\d+)\s*pulgadas', text.lower())
                    if size_match:
                        return int(size_match.group(1))
            
            # Fallback: buscar en el título del producto
            title_element = soup.find('h1')
            if title_element:
                title_text = title_element.get_text()
                # Buscar patrones como "60", "55", etc. seguidos de pulgadas o comillas
                size_match = re.search(r'(\d+)["\']|(\d+)\s*pulgadas', title_text.lower())
                if size_match:
                    return int(size_match.group(1) or size_match.group(2))
            
            logger.warning("No se pudo extraer el tamaño de pantalla")
            return 0
            
        except Exception as e:
            logger.error(f"Error extrayendo tamaño: {e}")
            return 0
    
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extrae la calificación del producto."""
        try:
            # Selector específico para la calificación en Alkosto
            rating_element = soup.select_one('span.averageNumber')
            if rating_element:
                rating_text = rating_element.get_text(strip=True)
                # Convertir a float
                return float(rating_text)
            
            return None  # No hay calificación disponible
            
        except Exception as e:
            logger.error(f"Error extrayendo calificación: {e}")
            return None
    
    def _extract_brand(self, soup: BeautifulSoup) -> str:
        """Extrae la marca del producto desde el nombre."""
        try:
            # Obtener el nombre del producto
            title_element = soup.find('h1')
            if not title_element:
                title_element = soup.find('title')
            
            if title_element:
                title_text = title_element.get_text().upper()
                
                # Marcas comunes de TV en el mercado colombiano
                # IMPORTANTE: Ordenar por longitud (más largas primero) para evitar coincidencias parciales
                brands_colombia = [
                    'SAMSUNG', 'PANASONIC', 'HISENSE', 'CHALLENGER', 'PHILIPS', 
                    'SKYWORTH', 'TOSHIBA', 'KALLEY', 'VITRON', 'XIAOMI', 
                    'HUAWEI', 'SHARP', 'HAIER', 'COOCAA', 'SANKEY',
                    'SONY', 'ASUS', 'TCL', 'AOC', 'RCA', 'LG'  # LG al final para evitar match con "GoogLe"
                ]
                
                # Buscar cada marca en el título (palabras completas)
                words = title_text.split()
                for brand in brands_colombia:
                    if brand in words:  # Buscar palabra completa, no substring
                        return brand.capitalize()
                
                # Si no encontramos con palabras completas, buscar como substring
                # pero evitar falsos positivos comunes
                for brand in brands_colombia:
                    if brand in title_text and brand not in ['LG']:  # Excluir LG de substring search
                        return brand.capitalize()
                
                # Caso especial para LG (solo si es palabra completa o al inicio)
                if ' LG ' in title_text or title_text.startswith('LG '):
                    return 'Lg'
                
                # Si no encontramos marca conocida, intentar extraer la primera palabra
                # que podría ser una marca desconocida
                words = title_text.split()
                if len(words) > 1 and words[0] not in ['TV', 'SMART', 'TELEVISOR']:
                    return words[0].capitalize()
            
            logger.warning("No se pudo extraer la marca")
            return "Desconocida"
            
        except Exception as e:
            logger.error(f"Error extrayendo marca: {e}")
            return "Desconocida"
    
    def _extract_resolution(self, soup: BeautifulSoup) -> str:
        """Extrae la resolución del producto."""
        try:
            # Buscar en las especificaciones del producto
            spec_elements = soup.find_all('div', class_='new-container__table__classifications___type__item_result')
            for element in spec_elements:
                text = element.get_text(strip=True).upper()
                # Buscar patrones de resolución
                if '4K' in text or 'UHD' in text:
                    return '4K'
                elif 'FHD' in text or 'FULL HD' in text:
                    return 'Full HD'
                elif 'HD' in text:
                    return 'HD'
            
            # Fallback: buscar en el título
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
            
            return 'HD'  # Valor por defecto
                
        except Exception as e:
            logger.error(f"Error extrayendo resolución: {e}")
            return 'HD'