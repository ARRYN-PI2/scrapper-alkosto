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

class AlkostoScraperAdapter(ScraperPort):
    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self._global_counter = 0

    def _with_page(self, url: str, page: int) -> str:
        """Add or modify page parameter in URL."""
        parts = list(urlparse(url))
        qs = parse_qs(parts[4])
        qs["page"] = [str(page)]
        parts[4] = urlencode(qs, doseq=True)
        return urlunparse(parts)

    def _sleep(self):
        lo, hi = REQUEST_DELAY_SECONDS
        time.sleep(random.uniform(lo, hi))

    def _get(self, url: str) -> str:
        r = self.session.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return r.text

    def _extract_state_json(self, html: str) -> Optional[dict]:
        """Extract embedded JSON state from HTML."""
        patterns = [
            r"window\.__PRELOADED_STATE__\s*=\s*(\{.*?\})\s*;\s*</script>",
            r"__STATE__\s*=\s*(\{.*?\})\s*;\s*</script>",
            r"__APOLLO_STATE__\s*=\s*(\{.*?\})\s*;\s*</script>",
            r'"__NEXT_DATA__"\s*:\s*(\{.*?\})\s*,',
            r'"__NEXT_DATA__"\s*:\s*(\{.*?\})\s*</script>',
        ]
        for pat in patterns:
            m = re.search(pat, html, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group(1))
                except json.JSONDecodeError:
                    cleaned = m.group(1).replace("\n", "").replace("\t", "")
                    try:
                        return json.loads(cleaned)
                    except Exception:
                        continue
        return None

    def _guess_items_from_state(self, state: dict) -> List[Dict[str, Any]]:
        """Extract product items from embedded state."""
        items: List[Dict[str, Any]] = []

        # Look for product objects with name, brand, price
        for v in (state.values() if isinstance(state, dict) else []):
            if isinstance(v, dict) and ("name" in v or "productName" in v):
                name = v.get("name") or v.get("productName") or ""
                brand = v.get("brand") or ""
                link = v.get("url") or v.get("linkText") or v.get("slug") or ""
                
                # Extract price and image info
                price, currency, image = None, None, ""
                try:
                    # Handle different price structures
                    if "price" in v:
                        price_info = v["price"]
                        if isinstance(price_info, dict):
                            price = price_info.get("value") or price_info.get("amount")
                            currency = price_info.get("currency") or "COP"
                        else:
                            price = price_info
                    
                    # Handle image
                    if "image" in v:
                        img_info = v["image"]
                        if isinstance(img_info, list) and img_info:
                            image = img_info[0]
                        elif isinstance(img_info, str):
                            image = img_info
                    
                    # Handle rating
                    rating = ""
                    if "rating" in v:
                        rating = str(v["rating"])
                    elif "aggregateRating" in v:
                        rating_info = v["aggregateRating"]
                        if isinstance(rating_info, dict):
                            rating = str(rating_info.get("ratingValue", ""))
                
                except Exception:
                    pass

                items.append({
                    "name": name,
                    "brand": brand,
                    "price": price,
                    "currency": currency or "COP",
                    "image": image,
                    "link": f"{BASE_HOST}/{link}" if link and not link.startswith("http") else link,
                    "rating": rating,
                    "details": v.get("description", ""),
                })

        return items

    def _is_product_url(self, url: str, categoria: str) -> bool:
        """Check if URL matches product patterns for the category."""
        if categoria not in EXPECTED_URLS:
            return False
        
        patterns = EXPECTED_URLS[categoria].get("patron_url", [])
        return any(pattern in url for pattern in patterns)

    def _guess_items_from_html(self, html: str, categoria: str) -> List[Dict[str, Any]]:
        """Extract product items from HTML as fallback."""
        soup = BeautifulSoup(html, "lxml")
        items: List[Dict[str, Any]] = []
        
        # Try multiple selectors for Alkosto
        selectors = [
            "a[href*='/p']",
            "a[data-testid*='product']",
            ".product-item a",
            ".item-product a",
            "[data-product-id] a",
        ]
        
        links_found = []
        for selector in selectors:
            links = soup.select(selector)
            if links:
                links_found.extend(links)
        
        # Remove duplicates
        seen_links = set()
        unique_links = []
        for link in links_found:
            href = link.get("href", "")
            if href and href not in seen_links:
                seen_links.add(href)
                unique_links.append(link)
        
        for link in unique_links:
            href = link.get("href", "")
            if not href:
                continue
            
            # Filter by category patterns
            if not self._is_product_url(href, categoria):
                continue
            
            # Extract product info
            title = ""
            # Try different title extraction methods
            title_sources = [
                link.get("title"),
                link.get("data-title"),
                link.get_text(strip=True) if link.get_text(strip=True) else None
            ]
            
            for title_src in title_sources:
                if title_src and title_src.strip():
                    title = title_src.strip()
                    break
            
            if not title:
                # Try to find title in nearby elements
                container = link.parent
                if container:
                    title_elem = container.select_one("[data-testid*='title'], .product-title, .item-name, h2, h3")
                    if title_elem:
                        title = title_elem.get_text(strip=True)
            
            if not title:
                continue
            
            # Extract image
            image = ""
            img = link.select_one("img")
            if img:
                image = img.get("src") or img.get("data-src") or img.get("data-lazy-src") or ""
            
            # Extract price
            price_text = ""
            container = link.parent
            if container:
                price_selectors = [
                    ".price",
                    ".selling-price",
                    "[class*='price']",
                    "[data-testid*='price']",
                    ".price-current"
                ]
                for price_sel in price_selectors:
                    price_elem = container.select_one(price_sel)
                    if price_elem:
                        price_text = price_elem.get_text(strip=True)
                        break
            
            # Ensure proper URL format
            link_url = href
            if link_url.startswith("/"):
                link_url = BASE_HOST + link_url
            
            # Ensure proper image URL format  
            image_url = image
            if image_url and image_url.startswith("/"):
                image_url = BASE_HOST + image_url

            items.append({
                "name": title,
                "brand": "",
                "price": None,
                "currency": "COP",
                "image": image_url,
                "link": link_url,
                "rating": "",
                "details": "",
                "price_text": price_text,
            })
        
        return items

    def _first_int_or_none(self, s: str) -> Optional[int]:
        s = s or ""
        m = re.search(r"(\d[\d\.\,\s]+)", s)
        if not m:
            return None
        num = m.group(1).replace(".", "").replace(" ", "").replace(",", "")
        try:
            return int(num)
        except Exception:
            return None

    def _infer_size(self, title: str) -> str:
        # Detect common sizes (inches for TVs, etc.)
        m = re.search(r"(\d{2}(?:\.\d)?)\s*(?:\"|pulg|pulgadas)", title, re.IGNORECASE)
        return f'{m.group(1)}"' if m else ""

    def scrape(self, categoria: str, page: int) -> Iterable[Producto]:
        if categoria not in EXPECTED_URLS:
            raise ValueError(f"Categoría no soportada: {categoria}")

        # Get the base URL for the category
        base_url = EXPECTED_URLS[categoria]["url"]
        url = self._with_page(base_url, page)
        
        html = self._get(url)

        # Try to extract from embedded state first
        state = self._extract_state_json(html)
        items = self._guess_items_from_state(state) if state else []
        
        # Fallback to HTML scraping
        if not items:
            items = self._guess_items_from_html(html, categoria)

        productos: List[Producto] = []

        for idx, it in enumerate(items, start=1):
            self._global_counter += 1
            
            titulo = (it.get("name") or "").strip()
            marca = (it.get("brand") or "").strip()
            img = (it.get("image") or "").strip()
            link = (it.get("link") or "").strip()
            rating = str(it.get("rating") or "").strip()
            details = (it.get("details") or "").strip()

            # Handle pricing
            precio_valor = it.get("price")
            moneda = it.get("currency") or "COP"
            precio_texto = it.get("price_text") or ""
            
            if precio_valor and not precio_texto:
                precio_texto = f"{moneda} {int(round(float(precio_valor)))}"
            if not precio_valor and precio_texto:
                precio_valor = self._first_int_or_none(precio_texto)

            # Infer size for relevant categories
            tam = ""
            if categoria in ["televisores"]:
                tam = self._infer_size(titulo)

            # Clean details
            details_cleaned = clean_html_details(details) if details else ""

            # Determine extraction status
            status = "OK"
            if not titulo:
                status = "MISSING_FIELDS"

            productos.append(Producto(
                contador_extraccion_total=self._global_counter,
                contador_extraccion=idx,
                titulo=titulo,
                marca=marca,
                precio_texto=precio_texto,
                precio_valor=precio_valor if isinstance(precio_valor, int) else (int(precio_valor) if isinstance(precio_valor, float) else None),
                moneda=moneda if precio_valor else None,
                tamaño=tam,
                calificacion=rating,
                detalles_adicionales=details_cleaned,
                fuente="alkosto.com",
                categoria=categoria,
                imagen=img,
                link=link if link.startswith("http") else (BASE_HOST + link if link else ""),
                pagina=page,
                fecha_extraccion=Producto.now_iso(),
                extraction_status=status
            ))

        self._sleep()
        return productos