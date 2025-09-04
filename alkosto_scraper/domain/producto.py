from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime

@dataclass
class Producto:
    contador_extraccion_total: int
    contador_extraccion: int
    titulo: str
    marca: str
    precio_texto: str
    precio_valor: Optional[int]
    moneda: Optional[str]
    tamaño: str
    calificacion: str
    detalles_adicionales: str
    fuente: str
    categoria: str
    imagen: str
    link: str
    pagina: int
    fecha_extraccion: str
    extraction_status: str = field(default="OK")

    @staticmethod
    def now_iso() -> str:
        return datetime.now().isoformat(timespec="seconds")

    def to_dict(self) -> dict:
        return asdict(self)