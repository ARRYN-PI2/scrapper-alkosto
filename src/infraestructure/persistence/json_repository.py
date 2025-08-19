import json
import os
from datetime import datetime
from typing import List, Dict, Any, Union
from pathlib import Path

from src.domain.entities.televisor import Televisor
from src.domain.entities.producto_generico import ProductoGenerico
from src.domain.repositories.television_repository import TelevisionRepository
from loguru import logger


class JsonRepository(TelevisionRepository):
    """
    Repositorio JSON expandido para múltiples categorías de productos.
    
    COMPATIBILIDAD: 100% compatible con código existente de televisores.
    NUEVAS CAPACIDADES: Maneja ProductoGenerico y múltiples categorías.
    """
    
    def __init__(self, base_path: str = "data"):
        """
        Inicializa el repositorio JSON.
        
        Args:
            base_path: Directorio base para almacenar archivos
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def save_televisions(self, products: List[Union[Televisor, ProductoGenerico]], source: str = "alkosto") -> str:
        """
        MÉTODO PRINCIPAL: Guarda productos (televisores o genéricos).
        
        Args:
            products: Lista de Televisor o ProductoGenerico
            source: Fuente de los datos
            
        Returns:
            Ruta del archivo guardado
        """
        # Detectar tipo de productos automáticamente
        if not products:
            logger.warning("⚠️ Lista de productos vacía")
            return ""
        
        primer_producto = products[0]
        es_generico = isinstance(primer_producto, ProductoGenerico)
        
        if es_generico:
            return self._save_productos_genericos(products, source)
        else:
            return self._save_televisores_original(products, source)
    
    def _save_productos_genericos(self, productos: List[ProductoGenerico], source: str) -> str:
        """
        Guarda productos genéricos con estructura expandida.
        """
        # Agrupar por categoría
        productos_por_categoria = {}
        for producto in productos:
            categoria = producto.categoria
            if categoria not in productos_por_categoria:
                productos_por_categoria[categoria] = []
            productos_por_categoria[categoria].append(producto)
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        categorias_str = "_".join(sorted(productos_por_categoria.keys()))
        filename = f"{source}_{categorias_str}_{timestamp}.json"
        filepath = self.base_path / filename
        
        # Crear estructura de datos expandida
        data = {
            "metadata": {
                "fuente": source,
                "fecha_scraping": datetime.now().isoformat(),
                "total_productos": len(productos),
                "categorias": list(productos_por_categoria.keys()),
                "scraper_version": "2.0_multicategoria",
                "estructura_version": "expandida",
                "estadisticas_por_categoria": {}
            },
            "productos": []
        }
        
        # Agregar estadísticas por categoría
        for categoria, prods_categoria in productos_por_categoria.items():
            stats = self._calculate_category_statistics(prods_categoria)
            data["metadata"]["estadisticas_por_categoria"][categoria] = stats
        
        # Convertir todos los productos a diccionario
        for producto in productos:
            data["productos"].append(producto.to_dict())
        
        # Agregar estadísticas generales
        data["metadata"]["estadisticas_generales"] = self._calculate_general_statistics(productos)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Productos genéricos guardados: {filepath}")
            logger.info(f"📊 Total: {len(productos)} productos en {len(productos_por_categoria)} categorías")
            
            # Log por categoría
            for categoria, prods in productos_por_categoria.items():
                logger.info(f"   📂 {categoria}: {len(prods)} productos")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Error guardando productos genéricos: {e}")
            raise
    
    def _save_televisores_original(self, televisores: List[Televisor], source: str) -> str:
        """
        Guarda televisores con estructura original (compatibilidad).
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{source}_televisores_{timestamp}.json"
        filepath = self.base_path / filename
        
        # Estructura original para compatibilidad
        data = {
            "metadata": {
                "fuente": source,
                "fecha_scraping": datetime.now().isoformat(),
                "total_productos": len(televisores),
                "scraper_version": "1.0_compatible",
                "estadisticas": self._calculate_tv_statistics(televisores)
            },
            "productos": [tv.to_dict() for tv in televisores]
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Televisores guardados (modo compatibilidad): {filepath}")
            logger.info(f"📊 Total: {len(televisores)} televisores")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Error guardando televisores: {e}")
            raise
    
    def load_televisions(self, filepath: str) -> List[Union[Televisor, ProductoGenerico]]:
        """
        Carga productos desde archivo JSON.
        Detecta automáticamente el formato y retorna el tipo apropiado.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get('metadata', {})
            productos_data = data.get('productos', [])
            
            # Detectar formato por versión del scraper
            version = metadata.get('scraper_version', '1.0')
            
            if version.startswith('2.0') or 'categoria' in productos_data[0] if productos_data else False:
                # Formato genérico
                productos = [ProductoGenerico.from_dict(prod) for prod in productos_data]
                logger.info(f"📂 Cargados {len(productos)} productos genéricos desde {filepath}")
            else:
                # Formato original (televisores)
                productos = [Televisor.from_dict(prod) for prod in productos_data]
                logger.info(f"📂 Cargados {len(productos)} televisores desde {filepath}")
            
            return productos
            
        except Exception as e:
            logger.error(f"❌ Error cargando desde {filepath}: {e}")
            raise
    
    def get_latest_file(self, source: str = "alkosto") -> str:
        """
        Obtiene el archivo más reciente para una fuente específica.
        """
        pattern = f"{source}_*.json"
        files = list(self.base_path.glob(pattern))
        
        if not files:
            return None
        
        # Retornar el archivo más reciente
        latest_file = max(files, key=os.path.getctime)
        return str(latest_file)
    
    def list_files(self, source: str = None) -> List[str]:
        """
        Lista archivos JSON disponibles.
        """
        if source:
            pattern = f"{source}_*.json"
        else:
            pattern = "*.json"
        
        files = list(self.base_path.glob(pattern))
        files.sort(key=os.path.getctime, reverse=True)
        
        return [str(f) for f in files]
    
    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """
        Obtiene información de un archivo JSON.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data.get('metadata', {})
            file_stat = Path(filepath).stat()
            
            info = {
                "archivo": filepath,
                "fuente": metadata.get('fuente', 'Desconocida'),
                "fecha_scraping": metadata.get('fecha_scraping', 'Desconocida'),
                "total_productos": metadata.get('total_productos', 0),
                "tamaño_archivo_kb": round(file_stat.st_size / 1024, 2),
                "fecha_creacion": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                "version_scraper": metadata.get('scraper_version', '1.0'),
                "estructura": metadata.get('estructura_version', 'original')
            }
            
            # Información específica por versión
            if 'categorias' in metadata:
                info["categorias"] = metadata['categorias']
                info["estadisticas_por_categoria"] = metadata.get('estadisticas_por_categoria', {})
            else:
                info["categorias"] = ["televisores"]
                info["estadisticas"] = metadata.get('estadisticas', {})
            
            return info
            
        except Exception as e:
            logger.error(f"Error obteniendo info de {filepath}: {e}")
            return {"error": str(e)}
    
    def _calculate_category_statistics(self, productos: List[ProductoGenerico]) -> Dict[str, Any]:
        """
        Calcula estadísticas para una categoría específica.
        """
        if not productos:
            return {}
        
        from collections import Counter
        
        precios = [p.precio for p in productos if p.precio > 0]
        marcas = [p.marca for p in productos]
        calificaciones = [p.calificacion for p in productos if p.calificacion is not None]
        
        stats = {
            "total_productos": len(productos),
            "precios": {
                "min": min(precios) if precios else 0,
                "max": max(precios) if precios else 0,
                "promedio": round(sum(precios) / len(precios), 2) if precios else 0,
                "productos_con_precio": len(precios)
            },
            "marcas_top_5": dict(Counter(marcas).most_common(5)),
            "calificaciones": {
                "promedio": round(sum(calificaciones) / len(calificaciones), 2) if calificaciones else 0,
                "productos_con_calificacion": len(calificaciones)
            },
            "productos_con_imagen": len([p for p in productos if p.imagen])
        }
        
        return stats
    
    def _calculate_general_statistics(self, productos: List[ProductoGenerico]) -> Dict[str, Any]:
        """
        Calcula estadísticas generales de todos los productos.
        """
        from collections import Counter
        
        categorias = [p.categoria for p in productos]
        fuentes = [p.fuente for p in productos]
        status = [p.extraction_status for p in productos]
        
        return {
            "productos_por_categoria": dict(Counter(categorias)),
            "productos_por_fuente": dict(Counter(fuentes)),
            "status_extraccion": dict(Counter(status)),
            "productos_con_extras": len([p for p in productos if p.atributos_extra])
        }
    
    def _calculate_tv_statistics(self, televisores: List[Televisor]) -> Dict[str, Any]:
        """
        Calcula estadísticas para televisores (compatibilidad).
        """
        if not televisores:
            return {}
        
        from collections import Counter
        
        precios = [tv.precio for tv in televisores if tv.precio > 0]
        tamanos = [tv.tamano_pulgadas for tv in televisores if tv.tamano_pulgadas > 0]
        marcas = [tv.marca for tv in televisores]
        resoluciones = [tv.resolucion for tv in televisores]
        calificaciones = [tv.calificacion for tv in televisores if tv.calificacion is not None]
        
        return {
            "precios": {
                "min": min(precios) if precios else 0,
                "max": max(precios) if precios else 0,
                "promedio": round(sum(precios) / len(precios), 2) if precios else 0
            },
            "tamanos": {
                "min": min(tamanos) if tamanos else 0,
                "max": max(tamanos) if tamanos else 0,
                "promedio": round(sum(tamanos) / len(tamanos), 1) if tamanos else 0
            },
            "marcas_top_5": dict(Counter(marcas).most_common(5)),
            "resoluciones": dict(Counter(resoluciones).most_common()),
            "calificaciones": {
                "promedio": round(sum(calificaciones) / len(calificaciones), 2) if calificaciones else 0,
                "total_con_calificacion": len(calificaciones)
            }
        }
    
    # === MÉTODOS PARA MÚLTIPLES CATEGORÍAS ===
    
    def save_by_category(self, productos_por_categoria: Dict[str, List[ProductoGenerico]], source: str = "alkosto") -> Dict[str, str]:
        """
        Guarda productos separados por categoría (archivos individuales).
        
        Args:
            productos_por_categoria: Dict con categoria -> lista de productos
            source: Fuente de los datos
            
        Returns:
            Dict con categoria -> ruta de archivo
        """
        archivos_guardados = {}
        
        for categoria, productos in productos_por_categoria.items():
            if productos:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{source}_{categoria}_{timestamp}.json"
                filepath = self.base_path / filename
                
                # Estructura para archivo individual por categoría
                data = {
                    "metadata": {
                        "fuente": source,
                        "categoria": categoria,
                        "fecha_scraping": datetime.now().isoformat(),
                        "total_productos": len(productos),
                        "estadisticas": self._calculate_category_statistics(productos)
                    },
                    "productos": [p.to_dict() for p in productos]
                }
                
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    archivos_guardados[categoria] = str(filepath)
                    logger.info(f"💾 {categoria}: {len(productos)} productos → {filepath}")
                    
                except Exception as e:
                    logger.error(f"❌ Error guardando {categoria}: {e}")
        
        return archivos_guardados
    
    def load_by_category(self, categoria: str, source: str = "alkosto") -> List[ProductoGenerico]:
        """
        Carga productos de una categoría específica.
        """
        pattern = f"{source}_{categoria}_*.json"
        files = list(self.base_path.glob(pattern))
        
        if not files:
            logger.warning(f"⚠️ No se encontraron archivos para {categoria}")
            return []
        
        # Cargar el más reciente
        latest_file = max(files, key=os.path.getctime)
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            productos_data = data.get('productos', [])
            productos = [ProductoGenerico.from_dict(prod) for prod in productos_data]
            
            logger.info(f"📂 Cargados {len(productos)} productos de {categoria}")
            return productos
            
        except Exception as e:
            logger.error(f"❌ Error cargando {categoria}: {e}")
            return []