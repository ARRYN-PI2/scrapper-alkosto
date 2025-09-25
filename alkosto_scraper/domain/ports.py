from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable
from .producto import Producto

class ScraperPort(ABC):
    @abstractmethod
    def scrape(self, categoria: str, page: int) -> Iterable[Producto]:
        ...

class RepositoryPort(ABC):
    @abstractmethod
    def persist(self, productos: Iterable[Producto]) -> None:
        ...