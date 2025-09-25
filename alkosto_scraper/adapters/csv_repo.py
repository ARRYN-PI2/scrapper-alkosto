from __future__ import annotations
import csv
from typing import Iterable
from pathlib import Path
from ..domain.producto import Producto
from ..domain.ports import RepositoryPort

class CsvRepositoryAdapter(RepositoryPort):
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_header()

    def _ensure_header(self):
        if not self.path.exists():
            with self.path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "contador_extraccion_total","contador_extraccion","titulo","marca",
                    "precio_texto","precio_valor","moneda","tamaño","calificacion",
                    "detalles_adicionales","fuente","categoria","imagen","link",
                    "pagina","fecha_extraccion","extraction_status"
                ])

    def persist(self, productos: Iterable[Producto]) -> None:
        with self.path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for p in productos:
                d = p.to_dict()
                writer.writerow([
                    d["contador_extraccion_total"], d["contador_extraccion"], d["titulo"], d["marca"],
                    d["precio_texto"], d["precio_valor"], d["moneda"], d["tamaño"], d["calificacion"],
                    d["detalles_adicionales"], d["fuente"], d["categoria"], d["imagen"], d["link"],
                    d["pagina"], d["fecha_extraccion"], d["extraction_status"]
                ])