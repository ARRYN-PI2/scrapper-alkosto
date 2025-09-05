# Scrapper Alkosto

Un scraper para extraer información de productos desde Alkosto.com.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

### Scraping por categoría

```bash
python -m alkosto_scraper.main scrape --categoria televisores --paginas 5 --output data/televisores.jsonl
```

### Categorías disponibles

- `televisores`: Smart TVs y televisores
- `celulares`: Smartphones y teléfonos
- `domotica`: Casa inteligente y domótica
- `lavado`: Lavadoras y secadoras
- `refrigeracion`: Neveras y refrigeradores
- `cocina`: Estufas, hornos y cocinas
- `audifonos`: Audífonos y auriculares
- `videojuegos`: Consolas y videojuegos
- `deportes`: Artículos deportivos

### Formatos de salida

- `.jsonl`: Un producto por línea en formato JSON
- `.csv`: Archivo CSV con columnas estructuradas

## Comandos por categoría

A continuación se muestran los comandos específicos para extraer productos de cada categoría disponible:

### Televisores
```bash
python -m alkosto_scraper.main scrape --categoria televisores --paginas 3 --output data/televisores.jsonl
```

### Celulares y Smartphones
```bash
python -m alkosto_scraper.main scrape --categoria celulares --paginas 2 --output data/celulares.jsonl
```

### Domótica y Casa Inteligente
```bash
python -m alkosto_scraper.main scrape --categoria domotica --paginas 2 --output data/domotica.jsonl
```

### Electrodomésticos de Lavado
```bash
python -m alkosto_scraper.main scrape --categoria lavado --paginas 2 --output data/lavado.jsonl
```

### Refrigeración
```bash
python -m alkosto_scraper.main scrape --categoria refrigeracion --paginas 2 --output data/refrigeracion.jsonl
```

### Cocina
```bash
python -m alkosto_scraper.main scrape --categoria cocina --paginas 2 --output data/cocina.jsonl
```

### Audífonos y Auriculares
```bash
python -m alkosto_scraper.main scrape --categoria audifonos --paginas 2 --output data/audifonos.jsonl
```

### Videojuegos y Consolas
```bash
python -m alkosto_scraper.main scrape --categoria videojuegos --paginas 2 --output data/videojuegos.jsonl
```

### Deportes y Fitness
```bash
python -m alkosto_scraper.main scrape --categoria deportes --paginas 2 --output data/deportes.jsonl
```

### Exportar a CSV
Para cualquier categoría, puedes cambiar la extensión a `.csv` para obtener un archivo CSV:
```bash
python -m alkosto_scraper.main scrape --categoria televisores --paginas 2 --output data/televisores.csv
```

### Usar adaptador legacy (HTML)
Si necesitas usar el adaptador HTML anterior por compatibilidad:
```bash
python -m alkosto_scraper.main scrape --categoria televisores --paginas 1 --output data/televisores.jsonl --legacy
```

## Estructura del proyecto

```
alkosto_scraper/
├── domain/          # Modelos de dominio
├── adapters/        # Adaptadores para scraping y persistencia
├── application/     # Casos de uso
└── utils/          # Utilidades y helpers
```

## Estructura del producto

Cada producto extraído contiene la siguiente información:

- `contador_extraccion_total`: Contador global de extracción
- `contador_extraccion`: Contador por página
- `titulo`: Nombre del producto
- `marca`: Marca del producto
- `precio_texto`: Precio como texto original
- `precio_valor`: Valor numérico del precio
- `moneda`: Moneda (COP)
- `tamaño`: Tamaño (para TVs, etc.)
- `calificacion`: Calificación del producto
- `detalles_adicionales`: Descripción adicional
- `fuente`: "alkosto.com"
- `categoria`: Categoría del producto
- `imagen`: URL de la imagen
- `link`: URL del producto
- `pagina`: Número de página
- `fecha_extraccion`: Fecha de extracción
- `extraction_status`: Estado de la extracción

## Tecnología

Este scraper utiliza la **API de Algolia** de Alkosto para obtener datos de productos de manera eficiente y precisa. Esto garantiza:

- ✅ **Datos reales y actualizados** directamente de la base de datos de productos
- ✅ **Mayor velocidad** comparado con el parsing HTML tradicional  
- ✅ **Información completa** con todos los campos disponibles
- ✅ **Estabilidad** ante cambios en el diseño del sitio web

El adaptador HTML legacy está disponible como respaldo usando el flag `--legacy`.