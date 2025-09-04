from __future__ import annotations
import argparse
from pathlib import Path

from .config import EXPECTED_URLS
from .adapters.alkosto_scraper_adapter import AlkostoScraperAdapter
from .adapters.alkosto_algolia_adapter import AlkostoAlgoliaAdapter
from .adapters.json_repo import JsonRepositoryAdapter
from .adapters.csv_repo import CsvRepositoryAdapter
from .application.scrape_usecase import ScrapeCategoryUseCase

def _make_repo(output: str):
    out = Path(output)
    if out.suffix.lower() == ".csv":
        return CsvRepositoryAdapter(str(out))
    return JsonRepositoryAdapter(str(out if out.suffix.lower()==".jsonl" else out.with_suffix(".jsonl")))

def main():
    parser = argparse.ArgumentParser(description="Scraper Alkosto.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scrape", help="Extraer productos por categoría")
    s.add_argument("--categoria", required=True, choices=sorted(EXPECTED_URLS.keys()), help="Categoría a scrapear")
    s.add_argument("--paginas", type=int, default=1, help="Numero de páginas a extraer (>=1)")
    s.add_argument("--output", required=True, help="Ruta de salida (.jsonl o .csv)")
    s.add_argument("--legacy", action="store_true", help="Usar adaptador HTML legacy en lugar de Algolia API")

    args = parser.parse_args()

    if args.cmd == "scrape":
        # Usar el adaptador de Algolia por defecto (más eficiente y preciso)
        if args.legacy:
            scraper = AlkostoScraperAdapter()
            print("🔍 Usando adaptador HTML (legacy)")
        else:
            scraper = AlkostoAlgoliaAdapter()
            print("🔍 Usando adaptador Algolia (recomendado)")
            
        repo = _make_repo(args.output)
        usecase = ScrapeCategoryUseCase(scraper, repo)
        usecase.run(args.categoria, pages=max(1, int(args.paginas)))

if __name__ == "__main__":
    main()