EXPECTED_URLS = {
    "televisores": {
        "url": "https://www.alkosto.com/tv/smart-tv/c/BI_120_ALKOS",
        "patron_url": ['/tv-', '/television-', '/smart-tv-', '-tv-', '/pantalla-'],
    },
    "celulares": {
        "url": "https://www.alkosto.com/celulares/smartphones/c/BI_101_ALKOS",
        "patron_url": ['/celular-', '/smartphone-', '/telefono-', '/iphone-', '/samsung-', '/motorola-', '/xiaomi-'],
    },
    "domotica": {
        "url": "https://www.alkosto.com/casa-inteligente-domotica/c/BI_CAIN_ALKOS",
        "patron_url": ['/casa-', '/inteligente-', '/domotica-', '/sensor-', '/camara-'],
    },
    "lavado": {
        "url": "https://www.alkosto.com/electrodomesticos/grandes-electrodomesticos/lavado/c/BI_0600_ALKOS",
        "patron_url": ['/lavadora-', '/secadora-'],
    },
    "refrigeracion": {
        "url": "https://www.alkosto.com/electrodomesticos/grandes-electrodomesticos/refrigeracion/c/BI_0610_ALKOS",
        "patron_url": ['/nevera-', '/refrigerador-', '/congelador-'],
    },
    "cocina": {
        "url": "https://www.alkosto.com/electrodomesticos/grandes-electrodomesticos/cocina/c/BI_0580_ALKOS",
        "patron_url": ['/estufa-', '/horno-', '/cocina-', '/microondas-'],
    },
    "audifonos": {
        "url": "https://www.alkosto.com/audio/audifonos/c/BI_111_ALKOS",
        "patron_url": ['/audifono-', '/headphone-', '/auricular-'],
    },
    "videojuegos": {
        "url": "https://www.alkosto.com/videojuegos/c/BI_VIJU_ALKOS",
        "patron_url": ['/juego-', '/consola-', '/videojuego-', '/playstation-', '/xbox-', '/nintendo-'],
    },
    "deportes": {
        "url": "https://www.alkosto.com/deportes/c/BI_DEPO_ALKOS",
        "patron_url": ['/deporte-', '/ejercicio-', '/fitness-', '/bicicleta-'],
    }
}

BASE_HOST = "https://www.alkosto.com"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-CO,es;q=0.9",
}
TIMEOUT = 25
REQUEST_DELAY_SECONDS = (1.0, 2.0)  # min, max