from __future__ import annotations
from typing import Iterable
from ..domain.ports import ScraperPort, RepositoryPort

class ScrapeCategoryUseCase:
    def __init__(self, scraper: ScraperPort, repo: RepositoryPort):
        self.scraper = scraper
        self.repo = repo

    def run(self, categoria: str, pages: int = 1) -> None:
        for p in range(1, pages + 1):
            productos = list(self.scraper.scrape(categoria, p))
            if not productos:
                continue
            self.repo.persist(productos)