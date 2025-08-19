from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from src.domain.entities.televisor import Televisor


@dataclass
class ProductoGenerico:
    """
    Entidad genérica para cualquier producto de Alkosto.
    
    ATRIBUTOS UNIVERSALES (según tu lista):
    - precio, marca, tamaño, calificacion, imagen
    - url_producto, fuente, categoria, nombre
    - timestamp_extraccion, extraction_status, contador_extraccion
    
    COMPATIBILIDAD: 100% compatible con código existente de televisores
    """
    
    # === ATRIBUTOS PRINCIPALES (según tu lista) ===
    nombre: str
    precio: float
    marca: str
    categoria: str  # televisores, celulares, domotica, etc.
    url_producto: str
    fuente: str = "alkosto"
    
    # === ATRIBUTOS OPCIONALES (pueden ser null si no aplican) ===
    calificacion: Optional[float] = None
    tamaño: Optional[str] = None  # "55 pulgadas", "6.1 GB", "15 kg", etc.
    imagen: Optional[str] = None
    
    # === METADATOS DE EXTRACCIÓN ===
    timestamp_extraccion: datetime = field(default_factory=datetime.now)
    extraction_status: str = "success"  # success, partial, failed
    contador_extraccion: int = 1
    
    # === ATRIBUTOS ESPECÍFICOS POR CATEGORÍA ===
    atributos_extra: Dict[str, Any] = field(default_factory=dict)
    
    def agregar_atributo_extra(self, clave: str, valor: Any):
        """Agrega un atributo específico de la categoría."""
        self.atributos_extra[clave] = valor
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte a diccionario para JSON.
        TODOS los atributos de tu lista, algunos pueden ser null.
        """
        return {
            # Atributos universales de tu lista
            "precio": self.precio,
            "marca": self.marca,
            "tamaño": self.tamaño,
            "calificacion": self.calificacion,
            "imagen": self.imagen,
            "url_producto": self.url_producto,
            "fuente": self.fuente,
            "categoria": self.categoria,
            "nombre": self.nombre,
            
            # Metadatos de extracción
            "timestamp_extraccion": self.timestamp_extraccion.isoformat(),
            "extraction_status": self.extraction_status,
            "contador_extraccion": self.contador_extraccion,
            
            # Específicos por categoría (para mantener flexibilidad)
            "atributos_extra": self.atributos_extra
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductoGenerico':
        """Crea instancia desde diccionario."""
        return cls(
            nombre=data["nombre"],
            precio=data["precio"],
            marca=data["marca"],
            categoria=data["categoria"],
            url_producto=data["url_producto"],
            fuente=data.get("fuente", "alkosto"),
            calificacion=data.get("calificacion"),
            tamaño=data.get("tamaño"),
            imagen=data.get("imagen"),
            timestamp_extraccion=datetime.fromisoformat(data.get("timestamp_extraccion", datetime.now().isoformat())),
            extraction_status=data.get("extraction_status", "success"),
            contador_extraccion=data.get("contador_extraccion", 1),
            atributos_extra=data.get("atributos_extra", {})
        )
    
    def to_televisor(self) -> Televisor:
        """
        COMPATIBILIDAD: Convierte a Televisor para código existente.
        """
        tamano_pulgadas = self.atributos_extra.get('tamano_pulgadas', 0)
        resolucion = self.atributos_extra.get('resolucion', 'HD')
        
        return Televisor(
            nombre=self.nombre,
            precio=self.precio,
            tamano_pulgadas=tamano_pulgadas,
            calificacion=self.calificacion,
            marca=self.marca,
            resolucion=resolucion,
            pagina_fuente=self.fuente,
            url_producto=self.url_producto
        )
    
    def __str__(self) -> str:
        """Representación string universal."""
        calificacion_str = f"★{self.calificacion}" if self.calificacion else "Sin calificación"
        tamaño_str = f" {self.tamaño}" if self.tamaño else ""
        return f"{self.marca}{tamaño_str} - ${self.precio:,.0f} ({calificacion_str}) - {self.categoria} - {self.fuente}"


def get_categoria_config(categoria: str) -> Dict[str, Any]:
    """
    Configuración específica por categoría según tus URLs.
    """
    configs = {
        "televisores": {
            "url": "https://www.alkosto.com/tv/smart-tv/c/BI_120_ALKOS",
            "patron_url": ['/tv-', '/television-', '/smart-tv-', '-tv-', '/pantalla-'],
            "max_productos_esperados": 200
        },
        "celulares": {
            "url": "https://www.alkosto.com/celulares/smartphones/c/BI_101_ALKOS",
            "patron_url": ['/celular-', '/smartphone-', '/telefono-', '/iphone-', '/samsung-', '/motorola-', '/xiaomi-'],
            "max_productos_esperados": 300
        },
        "domotica": {
            "url": "https://www.alkosto.com/casa-inteligente-domotica/c/BI_CAIN_ALKOS",
            "patron_url": ['/casa-', '/inteligente-', '/domotica-', '/sensor-', '/camara-'],
            "max_productos_esperados": 150
        },
        "lavado": {
            "url": "https://www.alkosto.com/electrodomesticos/grandes-electrodomesticos/lavado/c/BI_0600_ALKOS",
            "patron_url": ['/lavadora-', '/secadora-'],
            "max_productos_esperados": 100
        },
        "refrigeracion": {
            "url": "https://www.alkosto.com/electrodomesticos/grandes-electrodomesticos/refrigeracion/c/BI_0610_ALKOS",
            "patron_url": ['/nevera-', '/refrigerador-', '/congelador-'],
            "max_productos_esperados": 150
        },
        "cocina": {
            "url": "https://www.alkosto.com/electrodomesticos/grandes-electrodomesticos/cocina/c/BI_0580_ALKOS",
            "patron_url": ['/estufa-', '/horno-', '/cocina-', '/microondas-'],
            "max_productos_esperados": 120
        },
        "audifonos": {
            "url": "https://www.alkosto.com/audio/audifonos/c/BI_111_ALKOS",
            "patron_url": ['/audifono-', '/headphone-', '/auricular-'],
            "max_productos_esperados": 200
        },
        "videojuegos": {
            "url": "https://www.alkosto.com/videojuegos/c/BI_VIJU_ALKOS",
            "patron_url": ['/juego-', '/consola-', '/videojuego-', '/playstation-', '/xbox-', '/nintendo-'],
            "max_productos_esperados": 500
        },
        "deportes": {
            "url": "https://www.alkosto.com/deportes/c/BI_DEPO_ALKOS",
            "patron_url": ['/deporte-', '/ejercicio-', '/fitness-', '/bicicleta-'],
            "max_productos_esperados": 300
        }
    }
    
    return configs.get(categoria.lower())