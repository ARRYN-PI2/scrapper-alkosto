"""
Adaptador mejorado para Alkosto que usa la API de Algolia directamente.
"""
from __future__ import annotations
import re, json, time, random
from typing import Iterable, List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import requests
from bs4 import BeautifulSoup

from ..domain.producto import Producto
from ..domain.ports import ScraperPort
from ..config import EXPECTED_URLS, BASE_HOST, DEFAULT_HEADERS, TIMEOUT, REQUEST_DELAY_SECONDS
from ..utils.html_formatter import clean_html_details


class AlkostoAlgoliaAdapter(ScraperPort):
    """Adaptador que usa la API de Algolia de Alkosto para obtener productos reales."""
    
    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self._global_counter = 0
        
        # Configuración de Algolia extraída del sitio web
        self.algolia_config = {
            "applicationId": "QX5IPS1B1Q",
            "apiKey": "7a8800d62203ee3a9ff1cdf74f99b268",
            "indexName": "alkostoIndexAlgoliaPRD"
        }
        
        # Mapeo de categorías a sus códigos en Algolia
        self.category_codes = {
            "televisores": "BI_120_ALKOS",
            "celulares": "BI_101_ALKOS", 
            "domotica": "BI_CAIN_ALKOS",
            "lavado": "BI_0600_ALKOS",
            "refrigeracion": "BI_0610_ALKOS",
            "cocina": "BI_0580_ALKOS",
            "portatiles": "BI_104_ALKOS",
            "audifonos": "BI_111_ALKOS",
            "videojuegos": "BI_VIJU_ALKOS",
            "deportes": "BI_DEPO_ALKOS"
        }

    def _sleep(self):
        """Pausa entre requests."""
        lo, hi = REQUEST_DELAY_SECONDS
        time.sleep(random.uniform(lo, hi))

    def _search_algolia(self, categoria: str, page: int, hits_per_page: int = 50) -> Dict[str, Any]:
        """Buscar productos usando la API de Algolia."""
        
        # Mapeo de categorías a términos de búsqueda
        search_terms = {
            "televisores": "television tv smart",
            "celulares": "celular smartphone telefono",
            "domotica": "casa inteligente domotica sensor",
            "lavado": "lavadora secadora",
            "refrigeracion": "nevera refrigerador congelador",
            "cocina": "estufa horno cocina microondas",
            "audifonos": "audifono headphone auricular",
            "videojuegos": "juego consola videojuego playstation xbox nintendo",
            "deportes": "deporte ejercicio fitness bicicleta",
            "portatiles": "laptop portatil notebook computador portatil computador-portatil"
        }
        
        search_query = search_terms.get(categoria, "")
        
        url = f"https://{self.algolia_config['applicationId']}-dsn.algolia.net/1/indexes/{self.algolia_config['indexName']}/query"
        
        # Parámetros de búsqueda para Algolia
        search_params = {
            "query": search_query,
            "hitsPerPage": hits_per_page,
            "page": page - 1,  # Algolia usa páginas basadas en 0
            "attributesToRetrieve": [
                "objectID",
                "name_text_es",  # Campo correcto para el nombre
                "name", 
                "productName",
                "marca_text",    # Campo correcto para la marca
                "brand",
                "brand_string_mv",
                "lowestprice_double",  # Campo correcto para el precio
                "discountprice_double",
                "pricevalue_cop_double",
                "baseprice_cop_string",
                "price",
                "url_es_string",  # Campo correcto para la URL
                "url",
                "linkText",
                "img-310wx310h_string",  # Campos de imagen
                "img-155wx155h_string",
                "image",
                "images",
                "averagescore_double",  # Campo correcto para rating
                "rating",
                "aggregateRating",
                "description",
                "shortDescription",
                "categorypath_string_mv",  # Campos de categoría
                "categoryname_text_es_mv",
                "category_string_mv",
                "instockflag_boolean",    # Disponibilidad
                "stocklevelstatus_string",
                "availability",
                "inStock"
            ]
        }
        
        # Solo agregar filtros de categoría si tenemos el código correcto
        category_code = self.category_codes.get(categoria)
        if category_code:
            search_params["facetFilters"] = [f"category_string_mv:{category_code}"]
        
        headers = {
            "X-Algolia-Application-Id": self.algolia_config["applicationId"],
            "X-Algolia-API-Key": self.algolia_config["apiKey"],
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.post(
                url, 
                headers=headers,
                data=json.dumps(search_params),
                timeout=TIMEOUT
            )
            response.raise_for_status()
            result = response.json()
            
            # Si no hay resultados con filtros, intentar sin filtros
            if result.get("nbHits", 0) == 0 and "facetFilters" in search_params:
                print(f"Sin resultados con filtros, intentando búsqueda libre para '{search_query}'...")
                search_params.pop("facetFilters", None)
                response = self.session.post(
                    url, 
                    headers=headers,
                    data=json.dumps(search_params),
                    timeout=TIMEOUT
                )
                response.raise_for_status()
                result = response.json()
            
            return result
            
        except Exception as e:
            print(f"Error en búsqueda Algolia: {e}")
            return {"hits": [], "nbHits": 0}

    def _extract_product_info(self, hit: Dict[str, Any], categoria: str) -> Dict[str, Any]:
        """Extraer información del producto desde un hit de Algolia."""
        # Nombre del producto - usar el campo correcto
        name = (hit.get("name_text_es") or 
                hit.get("name") or 
                hit.get("productName") or "")
        
        # Marca - usar el campo correcto  
        brand = (hit.get("marca_text") or 
                 hit.get("brand") or
                 (hit.get("brand_string_mv", [{}])[0] if hit.get("brand_string_mv") else "") or "")
        
        # Precio - usar los campos correctos
        price = None
        price_text = ""
        currency = "COP"
        
        # Priorizar lowestprice_double que parece ser el precio con descuento
        if "lowestprice_double" in hit and hit["lowestprice_double"]:
            price = int(hit["lowestprice_double"])
            price_text = f"COP {price:,}"
        elif "discountprice_double" in hit and hit["discountprice_double"]:
            price = int(hit["discountprice_double"])
            price_text = f"COP {price:,}"
        elif "pricevalue_cop_double" in hit and hit["pricevalue_cop_double"]:
            price = int(hit["pricevalue_cop_double"])
            price_text = f"COP {price:,}"
        elif "price" in hit:
            price_info = hit["price"]
            if isinstance(price_info, dict):
                price = price_info.get("value") or price_info.get("amount")
                currency = price_info.get("currency") or "COP"
            elif isinstance(price_info, (int, float)):
                price = int(price_info)
            
            if price:
                price_text = f"{currency} {price:,}"
        
        # URL del producto - usar el campo correcto
        link = hit.get("url_es_string") or hit.get("url") or hit.get("linkText") or ""
        if link and not link.startswith("http"):
            if link.startswith("/"):
                link = BASE_HOST + link
            else:
                link = f"{BASE_HOST}/{link}"
        
        # Imagen - usar los campos correctos de imagen
        image = ""
        if "img-310wx310h_string" in hit and hit["img-310wx310h_string"]:
            image = hit["img-310wx310h_string"]
        elif "img-155wx155h_string" in hit and hit["img-155wx155h_string"]:
            image = hit["img-155wx155h_string"]
        elif "images" in hit and isinstance(hit["images"], list) and hit["images"]:
            image = hit["images"][0]
        elif "image" in hit:
            image = hit["image"]
        
        if image and not image.startswith("http"):
            if image.startswith("/"):
                image = BASE_HOST + image
        
        # Rating - usar el campo correcto
        rating = ""
        if "averagescore_double" in hit and hit["averagescore_double"]:
            rating = str(hit["averagescore_double"])
        elif "aggregateRating" in hit:
            rating_info = hit["aggregateRating"]
            if isinstance(rating_info, dict):
                rating = str(rating_info.get("ratingValue", ""))
            else:
                rating = str(rating_info)
        elif "rating" in hit:
            rating = str(hit["rating"])
        
        # Descripción
        description = hit.get("description") or hit.get("shortDescription") or ""
        
        # Disponibilidad
        available = (hit.get("instockflag_boolean") or 
                    hit.get("availability") or 
                    hit.get("inStock") or
                    (hit.get("stocklevelstatus_string") == "inStock"))
        
        return {
            "objectID": hit.get("objectID", ""),
            "name": name,
            "brand": brand,
            "price": price,
            "price_text": price_text,
            "currency": currency,
            "link": link,
            "image": image,
            "rating": rating,
            "description": description,
            "available": available
        }

    def _infer_size(self, title: str) -> str:
        """Detectar tamaños comunes (pulgadas para TVs, etc.)."""
        m = re.search(r"(\d{2}(?:\.\d)?)\s*(?:\"|pulg|pulgadas)", title, re.IGNORECASE)
        return f'{m.group(1)}"' if m else ""

    def _is_relevant_product(self, hit: Dict[str, Any], categoria: str) -> bool:
        """Verificar si el producto es relevante para la categoría."""
        name = (hit.get("name_text_es") or 
                hit.get("name") or 
                hit.get("productName") or "").lower()
        
        # Palabras clave por categoría
        category_keywords = {
            "televisores": ["tv", "television", "smart", "led", "oled", "qled", "pantalla"],
            "celulares": ["celular", "smartphone", "telefono", "iphone", "samsung", "motorola", "xiaomi", "huawei"],
            "domotica": ["casa", "inteligente", "domotica", "sensor", "camara", "smart"],
            "lavado": ["lavadora", "secadora", "lavado"],
            "refrigeracion": ["nevera", "refrigerador", "congelador", "frigorifico"],
            "cocina": ["estufa", "horno", "cocina", "microondas", "cocineta"],
            "audifonos": ["audifono", "headphone", "auricular", "airpods", "beats"],
            "videojuegos": ["juego", "consola", "videojuego", "playstation", "xbox", "nintendo", "gaming"],
            "deportes": ["deporte", "ejercicio", "fitness", "bicicleta", "patineta", "gym"],
            "portatiles": ["laptop", "portatil", "notebook", "computador portatil", "chromebook", "lenovo", "hp", "asus", "acer", "dell"]
        }
        
        keywords = category_keywords.get(categoria, [])
        return any(keyword in name for keyword in keywords)

    def scrape(self, categoria: str, page: int) -> Iterable[Producto]:
        """Scraper principal usando Algolia."""
        if categoria not in self.category_codes:
            raise ValueError(f"Categoría no soportada: {categoria}")

        print(f"Buscando productos de {categoria} - página {page} usando Algolia API...")
        
        # Buscar en Algolia
        search_result = self._search_algolia(categoria, page)
        hits = search_result.get("hits", [])
        
        # Filtrar productos relevantes
        relevant_hits = [hit for hit in hits if self._is_relevant_product(hit, categoria)]
        
        print(f"Encontrados {len(hits)} productos totales, {len(relevant_hits)} relevantes en página {page}")
        
        productos: List[Producto] = []

        for idx, hit in enumerate(relevant_hits, start=1):
            self._global_counter += 1
            
            # Extraer información del producto
            product_info = self._extract_product_info(hit, categoria)
            
            titulo = product_info["name"].strip()
            marca = product_info["brand"].strip()
            precio_texto = product_info["price_text"]
            precio_valor = product_info["price"]
            moneda = product_info["currency"] if precio_valor else None
            link = product_info["link"]
            img = product_info["image"]
            rating = product_info["rating"]
            details = product_info["description"]

            # Inferir tamaño para categorías relevantes
            tam = ""
            if categoria in ["televisores"]:
                tam = self._infer_size(titulo)

            # Limpiar detalles
            details_cleaned = clean_html_details(details) if details else ""

            # Determinar estado de extracción
            status = "OK"
            if not titulo:
                status = "MISSING_FIELDS"
            elif not precio_valor:
                status = "MISSING_PRICE"

            productos.append(Producto(
                contador_extraccion_total=self._global_counter,
                contador_extraccion=idx,
                titulo=titulo,
                marca=marca,
                precio_texto=precio_texto,
                precio_valor=precio_valor,
                moneda=moneda,
                tamaño=tam,
                calificacion=rating,
                detalles_adicionales=details_cleaned,
                fuente="alkosto.com",
                categoria=categoria,
                imagen=img,
                link=link,
                pagina=page,
                fecha_extraccion=Producto.now_iso(),
                extraction_status=status
            ))

        self._sleep()
        return productos
