import re
from typing import List, Dict, Any, Optional
from src.domain.entities.televisor import Televisor
from loguru import logger


class DataProcessor:
    """
    Servicio de dominio para procesar y validar datos de televisores.
    
    RESPONSABILIDADES:
    - Limpiar y normalizar datos de televisores
    - Aplicar reglas de negocio para validación
    - Transformar datos crudos en datos consistentes
    - Detectar y corregir inconsistencias
    
    NOTA: Este es un SERVICIO DE DOMINIO porque contiene lógica de negocio
    que no pertenece específicamente a la entidad Televisor, pero que es
    fundamental para el funcionamiento del sistema.
    """
    
    def __init__(self):
        self.processed_count = 0
        self.errors_count = 0
        self.warnings_count = 0
        self.validation_rules = self._load_validation_rules()
    
    def process_televisions(self, raw_televisions: List[Televisor]) -> List[Televisor]:
        """
        Procesa una lista de televisores aplicando todas las reglas de negocio.
        
        Args:
            raw_televisions: Lista de televisores sin procesar
            
        Returns:
            Lista de televisores válidos y procesados
        """
        logger.info(f"🔄 Iniciando procesamiento de {len(raw_televisions)} televisores...")
        
        processed_televisions = []
        self._reset_counters()
        
        for i, tv in enumerate(raw_televisions):
            try:
                processed_tv = self._process_single_television(tv)
                
                if processed_tv and self._validate_television(processed_tv):
                    processed_televisions.append(processed_tv)
                    self.processed_count += 1
                else:
                    self.errors_count += 1
                    logger.warning(f"⚠️ Televisor inválido descartado: {tv.nombre[:50]}...")
                    
            except Exception as e:
                self.errors_count += 1
                logger.error(f"❌ Error procesando televisor {i}: {e}")
        
        self._log_processing_summary(len(raw_televisions))
        return processed_televisions
    
    def _process_single_television(self, tv: Televisor) -> Optional[Televisor]:
        """
        Aplica todas las transformaciones a un televisor individual.
        
        Args:
            tv: Televisor crudo
            
        Returns:
            Televisor procesado o None si no es procesable
        """
        try:
            # Crear nueva instancia con datos procesados
            processed_tv = Televisor(
                nombre=self._normalize_name(tv.nombre),
                precio=self._normalize_price(tv.precio),
                tamano_pulgadas=self._normalize_screen_size(tv.tamano_pulgadas),
                calificacion=self._normalize_rating(tv.calificacion),
                marca=self._normalize_brand(tv.marca),
                resolucion=self._normalize_resolution(tv.resolucion),
                pagina_fuente=tv.pagina_fuente,
                url_producto=self._clean_url(tv.url_producto)
            )
            
            return processed_tv
            
        except Exception as e:
            logger.error(f"Error procesando televisor individual: {e}")
            return None
    
    def _normalize_name(self, nombre: str) -> str:
        """REGLA DE NEGOCIO: Normalización de nombres de productos."""
        if not nombre:
            return "Producto sin nombre"
        
        # Limpiar espacios y caracteres especiales
        cleaned = re.sub(r'\s+', ' ', nombre.strip())
        cleaned = re.sub(r'[^\w\s\-"\'ñáéíóúÁÉÍÓÚ]', '', cleaned)
        
        # Aplicar reglas de capitalización específicas para TV
        corrections = {
            'Tv': 'TV', 'Hd': 'HD', '4k': '4K', '8k': '8K',
            'Uhd': 'UHD', 'Fhd': 'FHD', 'Led': 'LED',
            'Oled': 'OLED', 'Qled': 'QLED', 'Smart': 'Smart'
        }
        
        for wrong, correct in corrections.items():
            cleaned = re.sub(f'\\b{wrong}\\b', correct, cleaned, flags=re.IGNORECASE)
        
        return cleaned[:200]  # Límite de caracteres
    
    def _normalize_price(self, precio: float) -> float:
        """REGLA DE NEGOCIO: Validación y normalización de precios."""
        if precio is None or precio < 0:
            return 0.0
        
        # Reglas de negocio para precios válidos
        min_price = self.validation_rules["precio"]["minimo"]
        max_price = self.validation_rules["precio"]["maximo"]
        
        if precio < min_price:
            self.warnings_count += 1
            logger.warning(f"⚠️ Precio muy bajo: ${precio:,.0f} (mínimo esperado: ${min_price:,.0f})")
        
        if precio > max_price:
            self.warnings_count += 1
            logger.warning(f"⚠️ Precio muy alto: ${precio:,.0f} (máximo esperado: ${max_price:,.0f})")
        
        return round(precio, 2)
    
    def _normalize_screen_size(self, tamano: int) -> int:
        """REGLA DE NEGOCIO: Validación de tamaños de pantalla."""
        if tamano is None or tamano <= 0:
            return 0
        
        valid_sizes = self.validation_rules["tamanos"]["validos"]
        
        # Si el tamaño está en la lista de válidos, retornarlo
        if tamano in valid_sizes:
            return tamano
        
        # Si no está, buscar el más cercano
        closest_size = min(valid_sizes, key=lambda x: abs(x - tamano))
        
        if abs(closest_size - tamano) <= 2:  # Tolerancia de 2 pulgadas
            logger.info(f"📐 Tamaño ajustado: {tamano}\" → {closest_size}\"")
            return closest_size
        else:
            self.warnings_count += 1
            logger.warning(f"⚠️ Tamaño inusual: {tamano}\"")
            return tamano
    
    def _normalize_rating(self, calificacion: Optional[float]) -> Optional[float]:
        """REGLA DE NEGOCIO: Validación de calificaciones."""
        if calificacion is None:
            return None
        
        # Asegurar rango 0-5
        normalized = max(0.0, min(5.0, float(calificacion)))
        return round(normalized, 1)
    
    def _normalize_brand(self, marca: str) -> str:
        """REGLA DE NEGOCIO: Normalización de marcas."""
        if not marca:
            return "Desconocida"
        
        # Mapeo de marcas conocidas (regla de negocio)
        brand_mapping = self.validation_rules["marcas"]["mapeo"]
        
        marca_clean = marca.strip().title()
        
        # Buscar en el mapeo
        for canonical_brand, aliases in brand_mapping.items():
            if marca_clean.lower() in [alias.lower() for alias in aliases]:
                return canonical_brand
        
        return marca_clean
    
    def _normalize_resolution(self, resolucion: str) -> str:
        """REGLA DE NEGOCIO: Normalización de resoluciones."""
        if not resolucion:
            return "HD"
        
        resolution_mapping = self.validation_rules["resoluciones"]["mapeo"]
        resolucion_upper = resolucion.strip().upper()
        
        # Buscar coincidencia en el mapeo
        for standard_res, aliases in resolution_mapping.items():
            for alias in aliases:
                if alias in resolucion_upper:
                    return standard_res
        
        return "HD"  # Default
    
    def _clean_url(self, url: str) -> str:
        """REGLA DE NEGOCIO: Limpieza de URLs."""
        if not url:
            return ""
        
        # Remover parámetros de tracking
        url = url.split('?')[0]
        
        # Asegurar protocolo HTTPS
        if url.startswith('//'):
            url = 'https:' + url
        elif url.startswith('/'):
            url = 'https://www.alkosto.com' + url
        elif not url.startswith('http'):
            url = 'https://' + url
        
        return url
    
    def _validate_television(self, tv: Televisor) -> bool:
        """
        REGLA DE NEGOCIO: Validación final de un televisor.
        
        Define qué constituye un televisor válido para el sistema.
        """
        validation_rules = self.validation_rules["validacion"]
        
        # Validación de nombre
        if not tv.nombre or tv.nombre == "Producto sin nombre":
            return False
        
        # Validación de URL
        if not tv.url_producto:
            return False
        
        # Validación de datos mínimos
        if tv.precio <= 0 and tv.tamano_pulgadas <= 0:
            # Si no tiene precio ni tamaño, probablemente no es válido
            return False
        
        # Validación de rango de precios extremos
        if tv.precio > validation_rules["precio_maximo_absoluto"]:
            return False
        
        # Validación de tamaño extremo
        if tv.tamano_pulgadas > validation_rules["tamano_maximo_absoluto"]:
            return False
        
        return True
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """
        Carga las reglas de validación del dominio.
        
        Estas reglas definen qué constituye datos válidos en el negocio.
        """
        return {
            "precio": {
                "minimo": 100000,  # 100k COP mínimo
                "maximo": 20000000  # 20M COP máximo
            },
            "tamanos": {
                "validos": [24, 32, 40, 43, 50, 55, 58, 60, 65, 70, 75, 77, 82, 85, 98]
            },
            "marcas": {
                "mapeo": {
                    "Samsung": ["samsung", "samsumg"],
                    "LG": ["lg", "lg electronics"],
                    "Sony": ["sony", "sony pictures"],
                    "TCL": ["tcl", "t.c.l"],
                    "Hisense": ["hisense", "hi-sense"],
                    "Panasonic": ["panasonic", "panasonic corp"],
                    "Philips": ["philips", "phillips"],
                    "Xiaomi": ["xiaomi", "mi"],
                    "Challenger": ["challenger"],
                    "Kalley": ["kalley"],
                    "Toshiba": ["toshiba"]
                }
            },
            "resoluciones": {
                "mapeo": {
                    "8K": ["8K", "7680X4320"],
                    "4K": ["4K", "UHD", "ULTRA HD", "3840X2160"],
                    "Full HD": ["FULL HD", "FHD", "1080P", "1920X1080"],
                    "HD": ["HD", "720P", "1366X768", "1280X720"]
                }
            },
            "validacion": {
                "precio_maximo_absoluto": 50000000,  # 50M COP
                "tamano_maximo_absoluto": 120  # 120 pulgadas
            }
        }
    
    def _reset_counters(self):
        """Reinicia los contadores de procesamiento."""
        self.processed_count = 0
        self.errors_count = 0
        self.warnings_count = 0
    
    def _log_processing_summary(self, total_input: int):
        """Registra un resumen del procesamiento."""
        success_rate = (self.processed_count / total_input * 100) if total_input > 0 else 0
        
        logger.info(f"✅ Procesamiento completado:")
        logger.info(f"   📦 Exitosos: {self.processed_count}")
        logger.info(f"   ⚠️  Advertencias: {self.warnings_count}")
        logger.info(f"   ❌ Errores: {self.errors_count}")
        logger.info(f"   📊 Tasa de éxito: {success_rate:.1f}%")
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del último procesamiento.
        
        Returns:
            Diccionario con estadísticas del procesamiento
        """
        total = self.processed_count + self.errors_count
        return {
            "processed_count": self.processed_count,
            "errors_count": self.errors_count,
            "warnings_count": self.warnings_count,
            "success_rate": (self.processed_count / total * 100) if total > 0 else 0
        }