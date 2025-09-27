# Scrapper Alkosto - Documentación Técnica

## Descripción General

Este repositorio contiene un **web scraper especializado** para la extracción de información de productos desde el sitio web de Alkosto.com. El sistema está diseñado siguiendo principios de **arquitectura hexagonal (puertos y adaptadores)** y ofrece múltiples estrategias de extracción de datos.

## ¿Qué hace este código?

### Funcionalidades Principales

1. **Extracción de Productos**: Obtiene información detallada de productos de diferentes categorías disponibles en Alkosto.com
2. **Múltiples Estrategias de Scraping**:
   - **Algolia API** (Recomendado): Utiliza la API interna de búsqueda de Alkosto basada en Algolia
   - **HTML Scraping** (Legacy): Parsing tradicional del HTML del sitio web
   - **Híbrido**: Combina datos de Algolia con detalles adicionales del HTML

3. **Formatos de Salida Flexibles**:
    *Guardados en scrapper-alkosto/data*
   - **JSONL**: Un producto por línea en formato JSON
   - **CSV**: Archivo estructurado compatible con Excel y herramientas de análisis
   
   Cualquiera de estos 2 formatos son convertidos a **JSON** gracias a la clase alkosto_scraper/adapters/json_repo.py que toma el formato de salida y lo formatea a un nuevo Json mucho mas facil de leer, el cual se exporta a /data/ para guardar dichos Json.

4. **Categorías Soportadas**: 9 categorías de productos incluyendo televisores, celulares, electrodomésticos, etc.

## Arquitectura del Sistema

### Patrón de Diseño: Arquitectura Hexagonal

El proyecto implementa una arquitectura hexagonal limpia con las siguientes capas:

```
alkosto_scraper/
├── domain/              # 🎯 Núcleo del negocio
│   ├── producto.py      # Modelo de datos del producto
│   └── ports.py         # Interfaces/contratos
├── adapters/            # 🔌 Implementaciones específicas
│   ├── alkosto_algolia_adapter.py    # Scraper vía API Algolia
│   ├── alkosto_scraper_adapter.py    # Scraper HTML tradicional
│   ├── alkosto_hybrid_adapter.py     # Scraper híbrido
│   ├── json_repo.py                  # Persistencia JSONL
│   └── csv_repo.py                   # Persistencia CSV
├── application/         # 📋 Casos de uso
│   └── scrape_usecase.py # Orquestación del scraping
└── utils/              # 🛠️ Utilidades
    └── html_formatter.py # Limpieza de HTML
```

### Componentes Clave

#### 1. Dominio (`domain/`)
- **`Producto`**: Dataclass que define la estructura de un producto
- **`ScraperPort`**: Interfaz para adaptadores de scraping
- **`RepositoryPort`**: Interfaz para adaptadores de persistencia

#### 2. Adaptadores (`adapters/`)
- **`AlkostoAlgoliaAdapter`**: Implementación que consume la API de Algolia de Alkosto
- **`AlkostoScraperAdapter`**: Implementación tradicional con BeautifulSoup
- **`AlkostoHybridAdapter`**: Combina ambos enfoques
- **`JsonRepositoryAdapter`** y **`CsvRepositoryAdapter`**: Manejan la persistencia

#### 3. Aplicación (`application/`)
- **`ScrapeCategoryUseCase`**: Coordina el proceso de scraping y persistencia

## Tecnologías Utilizadas

### Dependencias Principales
- **`requests`**: Cliente HTTP para realizar peticiones web
- **`beautifulsoup4`**: Parser HTML para extracción de datos
- **`lxml`**: Parser XML/HTML de alto rendimiento

### Estrategia de Scraping Recomendada: Algolia API

El adaptador principal utiliza la **API de Algolia** que Alkosto usa internamente para su buscador:

```python
# Configuración de Algolia extraída del sitio
algolia_config = {
    "applicationId": "QX5IPS1B1Q",
    "apiKey": "7a8800d62203ee3a9ff1cdf74f99b268", 
    "indexName": "alkostoIndexAlgoliaPRD"
}
```

**Ventajas del enfoque Algolia**:
- ✅ **Datos estructurados**: Información ya procesada y normalizada
- ✅ **Mayor velocidad**: Sin necesidad de parsear HTML complejo
- ✅ **Estabilidad**: Resistente a cambios en el diseño del sitio
- ✅ **Datos completos**: Acceso a toda la información del catálogo

## Estructura de Datos Extraídos

Cada producto contiene los siguientes campos:

```python
@dataclass
class Producto:
    contador_extraccion_total: int    # Contador global
    contador_extraccion: int          # Contador por página  
    titulo: str                       # Nombre del producto
    marca: str                        # Marca
    precio_texto: str                 # Precio como texto ("COP 1,299,030")
    precio_valor: Optional[int]       # Valor numérico (1299030)
    moneda: Optional[str]             # Moneda ("COP")
    tamaño: str                       # Tamaño/dimensiones
    calificacion: str                 # Rating del producto
    detalles_adicionales: str         # Descripción adicional
    fuente: str                       # "alkosto.com"
    categoria: str                    # Categoría del producto
    imagen: str                       # URL de imagen
    link: str                         # URL del producto
    pagina: int                       # Número de página
    fecha_extraccion: str             # Timestamp ISO
    extraction_status: str            # Estado ("OK", "ERROR", etc.)
```

## Casos de Uso

### 1. Análisis de Mercado
- Monitoreo de precios de productos
- Análisis de catálogo por categorías
- Seguimiento de disponibilidad

### 2. Investigación de Productos
- Comparación de especificaciones
- Análisis de calificaciones y reviews
- Investigación de tendencias de marca

### 3. Data Science y Analytics
- Dataset para machine learning
- Análisis estadístico de precios
- Segmentación de productos

## Configuración y Categorías

El sistema soporta las siguientes categorías configuradas en `config.py`:

```python
EXPECTED_URLS = {
    "televisores": "Smart TVs y televisores",
    "celulares": "Smartphones y teléfonos", 
    "domotica": "Casa inteligente y domótica",
    "lavado": "Lavadoras y secadoras",
    "refrigeracion": "Neveras y refrigeradores", 
    "cocina": "Estufas, hornos y cocinas",
    "audifonos": "Audífonos y auriculares",
    "videojuegos": "Consolas y videojuegos",
    "deportes": "Artículos deportivos"
}
```

## Ejemplo de Uso Programático

```python
from alkosto_scraper.adapters.alkosto_algolia_adapter import AlkostoAlgoliaAdapter
from alkosto_scraper.adapters.json_repo import JsonRepositoryAdapter
from alkosto_scraper.application.scrape_usecase import ScrapeCategoryUseCase

# Configurar componentes
scraper = AlkostoAlgoliaAdapter()
repo = JsonRepositoryAdapter("productos.jsonl")
usecase = ScrapeCategoryUseCase(scraper, repo)

# Ejecutar scraping
usecase.run("televisores", pages=3)
```

## Características Técnicas Destacables

### 1. **Gestión de Rate Limiting**
- Delays aleatorios entre requests (1-2 segundos)
- Headers realistas para evitar detección
- Timeout configurables

### 2. **Robustez y Manejo de Errores**
- Múltiples adaptadores como fallback
- Logging de estados de extracción
- Reintentos automáticos

### 3. **Extensibilidad**
- Patrón de puertos permite agregar nuevos adaptadores fácilmente
- Nuevas categorías se configuran en un solo archivo
- Formatos de salida modulares

### 4. **Testing y Debugging**
- Scripts de test incluidos (`test_scraper.py`, `debug_scraper.py`)
- Logs detallados del proceso de extracción
- Validación de datos extraídos

## Flujo de Ejecución

1. **Configuración**: Se selecciona adaptador y repositorio según parámetros
2. **Scraping**: Se itera por las páginas solicitadas de la categoría
3. **Extracción**: Se obtienen productos usando la estrategia seleccionada
4. **Transformación**: Los datos se mapean al modelo `Producto`
5. **Persistencia**: Los productos se guardan en el formato especificado

Este scraper representa una solución robusta y escalable para la extracción de datos de e-commerce, implementada con buenas prácticas de ingeniería de software.
