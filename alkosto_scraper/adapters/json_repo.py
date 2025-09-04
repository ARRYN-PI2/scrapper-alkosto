from __future__ import annotations
import json
from typing import Iterable
from ..domain.ports import RepositoryPort
from ..domain.producto import Producto
from pathlib import Path

class JsonRepositoryAdapter(RepositoryPort):
    def __init__(self, path: str, generate_formatted: bool = True):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.generate_formatted = generate_formatted
        self.productos_buffer = []

    def persist(self, productos: Iterable[Producto]) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            for p in productos:
                producto_dict = p.to_dict()
                self.productos_buffer.append(producto_dict)
                f.write(json.dumps(producto_dict, ensure_ascii=False) + "\n")
        
        if self.generate_formatted:
            self._generate_formatted_json()
    
    def _generate_formatted_json(self) -> None:
        """Genera un archivo JSON formateado con todos los productos"""
        if not self.productos_buffer:
            return
            
        all_productos = []
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            all_productos.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        
        formatted_path = self.path.with_name(self.path.stem + '_formatted.json')
        with formatted_path.open("w", encoding="utf-8") as f:
            json.dump(all_productos, f, indent=2, ensure_ascii=False)