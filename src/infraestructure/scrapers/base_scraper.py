from abc import ABC, abstractmethod
from typing import List
import time
import requests
from fake_useragent import UserAgent
from loguru import logger

from src.domain.entities.televisor import Televisor


class BaseScraper(ABC):
    """
    Clase base para todos los scrapers.
    
    Define la estructura común que deben seguir todos los scrapers
    (Alkosto, Falabella, Éxito, etc.)
    """
    
    def __init__(self, delay_between_requests: float = 2.0, max_retries: int = 3):
        """
        Inicializa el scraper base.
        
        Args:
            delay_between_requests: Segundos de pausa entre peticiones
            max_retries: Número máximo de reintentos si falla una petición
        """
        self.delay_between_requests = delay_between_requests
        self.max_retries = max_retries
        self.session = requests.Session()
        self.user_agent = UserAgent()
        
        # Headers básicos para parecer un navegador real
        self.session.headers.update({
            'User-Agent': self.user_agent.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def make_request(self, url: str) -> requests.Response:
        """
        Hace una petición HTTP con reintentos y manejo de errores.
        
        Args:
            url: URL a la que hacer la petición
            
        Returns:
            Response object de requests
            
        Raises:
            Exception: Si agota todos los reintentos
        """
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Haciendo petición a: {url} (intento {attempt + 1})")
                
                # Cambiar User-Agent en cada intento
                self.session.headers.update({'User-Agent': self.user_agent.random})
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()  # Lanza excepción si hay error HTTP
                
                # Pausa entre peticiones para ser respetuosos
                if self.delay_between_requests > 0:
                    time.sleep(self.delay_between_requests)
                
                return response
                
            except requests.RequestException as e:
                logger.warning(f"Error en intento {attempt + 1}: {e}")
                
                if attempt == self.max_retries:
                    logger.error(f"Agotados todos los reintentos para {url}")
                    raise Exception(f"No se pudo acceder a {url} después de {self.max_retries + 1} intentos")
                
                # Pausa antes del siguiente intento
                time.sleep(2 ** attempt)  # Backoff exponencial: 1s, 2s, 4s...
    
    @abstractmethod
    def get_product_urls(self, max_pages: int = 1) -> List[str]:
        """
        Obtiene las URLs de todos los productos de televisores.
        
        Args:
            max_pages: Número máximo de páginas a recorrer
            
        Returns:
            Lista de URLs de productos
        """
        pass
    
    @abstractmethod
    def scrape_product(self, product_url: str) -> Televisor:
        """
        Extrae la información de un producto específico.
        
        Args:
            product_url: URL del producto a scrapear
            
        Returns:
            Objeto Televisor con los datos extraídos
        """
        pass
    
    def scrape_all_products(self, max_pages: int = 1) -> List[Televisor]:
        """
        Método principal que hace el scraping completo.
        
        Args:
            max_pages: Número máximo de páginas a recorrer
            
        Returns:
            Lista de objetos Televisor
        """
        logger.info(f"Iniciando scraping de {self.__class__.__name__}")
        
        # 1. Obtener todas las URLs de productos
        product_urls = self.get_product_urls(max_pages)
        logger.info(f"Encontradas {len(product_urls)} URLs de productos")
        
        # 2. Scrapear cada producto
        televisores = []
        for i, url in enumerate(product_urls, 1):
            try:
                logger.info(f"Scrapeando producto {i}/{len(product_urls)}: {url}")
                televisor = self.scrape_product(url)
                televisores.append(televisor)
                
            except Exception as e:
                logger.error(f"Error scrapeando {url}: {e}")
                continue  # Continúa con el siguiente producto
        
        logger.info(f"Scraping completado. {len(televisores)} productos extraídos exitosamente")
        return televisores