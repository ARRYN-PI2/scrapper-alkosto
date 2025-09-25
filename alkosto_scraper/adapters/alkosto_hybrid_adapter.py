from __future__ import annotations
import time, random
from typing import Iterable, List
from ..domain.producto import Producto
from ..domain.ports import ScraperPort
from ..config import REQUEST_DELAY_SECONDS
from .alkosto_algolia_adapter import AlkostoAlgoliaAdapter
from .alkosto_scraper_adapter import AlkostoScraperAdapter

class AlkostoHybridAdapter(ScraperPort):
    """
    Adaptador híbrido que combina Algolia para encontrar productos
    y scraping HTML para obtener detalles adicionales.
    """
    
    def __init__(self, session=None):
        self.algolia_adapter = AlkostoAlgoliaAdapter(session)
        self.scraper_adapter = AlkostoScraperAdapter(session)
    
    def _sleep(self):
        lo, hi = REQUEST_DELAY_SECONDS
        time.sleep(random.uniform(lo, hi))
    
    def scrape(self, categoria: str, page: int) -> Iterable[Producto]:
        print(f"🔄 Usando adaptador híbrido: Algolia + detalles HTML")
        
        # Usar Algolia para obtener productos
        productos_algolia = list(self.algolia_adapter.scrape(categoria, page))
        
        print(f"📦 Obtenidos {len(productos_algolia)} productos de Algolia")
        
        productos_enriquecidos = []
        
        for i, producto in enumerate(productos_algolia, 1):
            print(f"🔍 Extrayendo detalles {i}/{len(productos_algolia)}: {producto.titulo[:50]}...")
            
            # Extraer detalles adicionales del HTML si hay link
            detalles_adicionales = ""
            if producto.link and producto.link.startswith("http"):
                try:
                    detalles_adicionales = self.scraper_adapter._extract_product_details(producto.link)
                except Exception as e:
                    print(f"   ⚠️  Error extrayendo detalles: {e}")
            
            # Crear nuevo producto con detalles enriquecidos
            producto_enriquecido = Producto(
                contador_extraccion_total=producto.contador_extraccion_total,
                contador_extraccion=producto.contador_extraccion,
                titulo=producto.titulo,
                marca=producto.marca,
                precio_texto=producto.precio_texto,
                precio_valor=producto.precio_valor,
                moneda=producto.moneda,
                tamaño=producto.tamaño,
                calificacion=producto.calificacion,
                detalles_adicionales=detalles_adicionales,  # Detalles enriquecidos
                fuente=producto.fuente,
                categoria=producto.categoria,
                imagen=producto.imagen,
                link=producto.link,
                pagina=producto.pagina,
                fecha_extraccion=producto.fecha_extraccion,
                extraction_status=producto.extraction_status
            )
            
            productos_enriquecidos.append(producto_enriquecido)
            
            # Sleep para no sobrecargar el servidor
            self._sleep()
        
        print(f"✅ Completado: {len(productos_enriquecidos)} productos con detalles")
        return productos_enriquecidos
