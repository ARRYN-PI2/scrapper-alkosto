from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Televisor:
    """
    Modelo de datos que representa un televisor.
    
    Esta clase define exactamente la información que necesitamos de cada televisor
    para hacer comparaciones entre diferentes tiendas.
    """
    
    nombre: str                        # Nombre completo del televisor
    precio: float                      # Precio del televisor
    tamano_pulgadas: int              # Tamaño en pulgadas (ej: 55, 65, 75)
    calificacion: Optional[float]     # Calificación en puntos decimales (ej: 4.5)
    marca: str                        # Marca (Samsung, LG, Sony, etc.)
    resolucion: str                   # Resolución (HD, Full HD, 4K, 8K)
    pagina_fuente: str                # Página fuente (alkosto, falabella, exito)
    url_producto: str                 # URL del producto
    
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el objeto Televisor a un diccionario.
        Útil para guardar en JSON o MongoDB.
        """
        return {
            'nombre': self.nombre,
            'precio': self.precio,
            'tamano_pulgadas': self.tamano_pulgadas,
            'calificacion': self.calificacion,
            'marca': self.marca,
            'resolucion': self.resolucion,
            'pagina_fuente': self.pagina_fuente,
            'url_producto': self.url_producto
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Televisor':
        """
        Crea un objeto Televisor desde un diccionario.
        Útil para cargar desde JSON o MongoDB.
        """
        return cls(
            nombre=data['nombre'],
            precio=data['precio'],
            tamano_pulgadas=data['tamano_pulgadas'],
            calificacion=data.get('calificacion'),  # Puede ser None
            marca=data['marca'],
            resolucion=data['resolucion'],
            pagina_fuente=data['pagina_fuente'],
            url_producto=data['url_producto']
        )
    
    def __str__(self) -> str:
        """
        Representación en string del televisor para debugging.
        """
        calificacion_str = f"★{self.calificacion}" if self.calificacion else "Sin calificación"
        return f"{self.marca} {self.tamano_pulgadas}\" {self.resolucion} - ${self.precio:,.0f} ({calificacion_str}) - {self.pagina_fuente}"